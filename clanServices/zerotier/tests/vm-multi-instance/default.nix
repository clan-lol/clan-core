# Minimal multi-instance test: two independent ZeroTier networks on overlapping machines.
#
# Topology:
#   net-a: alpha=controller+moon, beta=peer
#   net-b: beta=controller+moon, alpha=peer
#
# Both machines join both networks and must get unique IPs on each.
# The test driver assigns IPs alphabetically: alpha=192.168.1.1, beta=192.168.1.2
# This is a bit leaky, but we need to know the IPs;
# If the test driver would allow us to define the IP beforehand...
{
  name = "zerotier-multi-instance";

  clan = {
    test.useContainers = false;
    directory = ./.;
    inventory = {

      machines.alpha = { };
      machines.beta = { };

      instances."net-a" = {
        module.name = "zerotier";
        module.input = "self";

        roles.peer.tags.all = { };
        roles.controller.machines.alpha = { };
        roles.moon.machines.alpha.settings.stableEndpoints = [ "192.168.1.1/9993" ];
      };

      instances."net-b" = {
        module.name = "zerotier";
        module.input = "self";

        roles.peer.tags.all = { };
        roles.controller.machines.beta = { };
        roles.moon.machines.beta.settings.stableEndpoints = [ "192.168.1.2/9993" ];
      };
    };
  };

  testScript =
    { nodes, ... }:
    let
      ipOf =
        machine: instance:
        nodes.${machine}.clan.core.vars.generators."zerotier-ip-${machine}-${instance}".files.ip.value;
    in
    ''
      import json

      machines = [alpha, beta]

      expected_ips = {
          "alpha": {
              "net-a": "${ipOf "alpha" "net-a"}",
              "net-b": "${ipOf "alpha" "net-b"}",
          },
          "beta": {
              "net-a": "${ipOf "beta" "net-a"}",
              "net-b": "${ipOf "beta" "net-b"}",
          },
      }

      def read_world_file(machine):
          """Read a moon's world file (before distribution, moons.d has only its own)."""
          files = machine.succeed("ls /var/lib/zerotier-one/moons.d/").strip().splitlines()
          assert len(files) == 1, f"{machine.name}: expected 1 moon file, got {files}"
          name = files[0]
          node_id = name.split(".")[0][-10:]
          b64 = machine.succeed(f"base64 -w0 /var/lib/zerotier-one/moons.d/{name}").strip()
          return name, node_id, b64

      # === Boot ===
      start_all()

      for m in machines:
          m.wait_for_unit("zerotierone.service")
          m.wait_for_open_port(9993)

      # === Moon exchange ===
      alpha_wf = read_world_file(alpha)
      beta_wf = read_world_file(beta)

      # Cross-install: each machine gets the other's moon world file
      for target, wf in [(beta, alpha_wf), (alpha, beta_wf)]:
          name, node_id, b64 = wf
          target.succeed("mkdir -p /var/lib/zerotier-one/moons.d")
          target.succeed(f"base64 -d <<< '{b64}' > /var/lib/zerotier-one/moons.d/{name}")
          target.succeed(f"zerotier-cli orbit {node_id} {node_id}")

      # === Verify both networks joined ===
      for m in machines:
          m.wait_until_succeeds(
              "test $(zerotier-cli listnetworks -j | jq 'length') -eq 2",
              timeout=120,
          )
          m.wait_until_succeeds(
              "test $(zerotier-cli listnetworks -j | jq '[.[] | select(.status == \"OK\")] | length') -eq 2",
              timeout=120,
          )

      # === Verify IPs assigned on both networks ===
      for m in machines:
          networks = json.loads(m.succeed("zerotier-cli listnetworks -j"))
          all_assigned = []
          for net in networks:
              all_assigned += [a.split("/")[0] for a in net.get("assignedAddresses", [])]
          for instance in ["net-a", "net-b"]:
              expected = expected_ips[m.name][instance]
              assert expected in all_assigned, (
                  f"{m.name}: {expected} (from {instance}) not in {all_assigned}"
              )

      # === Cross-ping on both networks ===
      for instance in ["net-a", "net-b"]:
          alpha.wait_until_succeeds(
              f"ping -6 -c 3 {expected_ips['beta'][instance]}",
              timeout=60,
          )
          beta.wait_until_succeeds(
              f"ping -6 -c 3 {expected_ips['alpha'][instance]}",
              timeout=60,
          )
    '';
}
