{
  name = "zerotier";

  clan = {
    test.useContainers = false;
    directory = ./.;
    inventory = {

      machines.controller = { };
      machines.moon = { };
      machines.peer1 = { };
      machines.peer2 = { };

      instances."zerotier" = {
        module.name = "zerotier";
        module.input = "self";

        roles.peer.tags.all = { };
        roles.controller.machines.controller = { };
        # QEMU VMs lack planet root servers, so peer discovery needs moon world
        # files with routable stableEndpoints (IPs assigned alphabetically by the
        # test driver: controller=.1, moon=.2, peer1=.3, peer2=.4). The controller
        # doubles as a moon so all machines can reach it; the dedicated moon
        # exercises the standalone code path.
        roles.moon.machines.controller.settings.stableEndpoints = [ "192.168.1.1/9993" ];
        roles.moon.machines.moon.settings.stableEndpoints = [ "192.168.1.2/9993" ];
      };
    };
  };

  testScript =
    { nodes, ... }:
    let
      ztIp =
        machine:
        nodes.${machine}.clan.core.vars.generators."zerotier-ip-${machine}-zerotier".files.ip.value;
    in
    ''
      import json

      machines = [controller, moon, peer1, peer2]
      machine_ips = {
          "controller": "${ztIp "controller"}",
          "moon": "${ztIp "moon"}",
          "peer1": "${ztIp "peer1"}",
          "peer2": "${ztIp "peer2"}",
      }

      def read_world_file(machine):
          """Read a moon's world file info. Call before any distribution
          so that moons.d contains only this machine's own file."""
          files = machine.succeed("ls /var/lib/zerotier-one/moons.d/").strip().splitlines()
          assert len(files) == 1, f"{machine.name}: expected 1 moon file, got {files}"
          name = files[0]
          node_id = name.split(".")[0][-10:]  # e.g. "000000865b0d5967.moon" -> "865b0d5967"
          b64 = machine.succeed(f"base64 -w0 /var/lib/zerotier-one/moons.d/{name}").strip()
          return name, node_id, b64

      # World file distribution is out-of-band; the module doesn't handle it.
      def install_world_file(targets, name, node_id, b64):
          """Install a world file on targets and trigger orbit so the daemon
          picks up the stableEndpoints."""
          for target in targets:
              target.succeed("mkdir -p /var/lib/zerotier-one/moons.d")
              target.succeed(
                  f"base64 -d <<< '{b64}'"
                  f" > /var/lib/zerotier-one/moons.d/{name}"
              )
              target.succeed(f"zerotier-cli orbit {node_id} {node_id}")

      # === Setup Phase ===
      start_all()

      for m in machines:
          m.wait_for_unit("zerotierone.service")
          m.wait_for_open_port(9993)

      controller.succeed(
          "systemctl show -p Result zerotier-inventory-autoaccept.service"
          " | grep -q success"
      )

      # === Moon setup ===
      for m in [controller, moon]:
          m.succeed("test -d /var/lib/zerotier-one/moons.d")
          m.succeed("test -f /var/lib/zerotier-one/moon.json")
          m.succeed("test -s /var/lib/zerotier-one/moon.json")

      # Read world files before distributing (each moons.d has only its own file).
      ctrl_wf = read_world_file(controller)
      moon_wf = read_world_file(moon)

      install_world_file([moon, peer1, peer2], *ctrl_wf)
      install_world_file([controller, peer1, peer2], *moon_wf)

      # === Assertions ===
      for m in machines:
          m.wait_until_succeeds(
              "zerotier-cli listnetworks | grep OK",
              timeout=120,
          )

      for m in machines:
          m.wait_until_succeeds(
              "zerotier-cli listpeers | grep MOON",
              timeout=120,
          )

      for m in machines:
          expected_ip = machine_ips[m.name]

          networks = json.loads(m.succeed("zerotier-cli listnetworks -j"))
          assert len(networks) == 1, f"{m.name}: expected 1 network, got {len(networks)}"
          assigned = [a.split("/")[0] for a in networks[0].get("assignedAddresses", [])]
          assert expected_ip in assigned, (
              f"{m.name}: {expected_ip} not in assigned addresses {assigned}"
          )

      for m1 in machines:
          for m2 in machines:
              if m1 != m2:
                  m1.wait_until_succeeds(
                      f"ping -6 -c 3 {machine_ips[m2.name]}",
                      timeout=60,
                  )

      for m in machines:
          m.succeed("ip link show | grep -q zt")
          m.succeed("ss -ulnp | grep -q 9993")
          m.succeed("ss -tlnp | grep -q 9993")
    '';
}
