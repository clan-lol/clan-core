{
  pkgs,
  self,
  clanLib,
  ...
}:
clanLib.test.makeTestClan {
  inherit pkgs self;
  nixosTest = (
    { lib, ... }:
    let
      machines = [
        "admin"
        "peer"
        "signer"
      ];
    in
    {
      name = "data-mesher";

      clan = {
        directory = ./.;
        inventory = {
          machines = lib.genAttrs machines (_: { });
          services = {
            data-mesher.default = {
              roles.peer.machines = [ "peer" ];
              roles.admin.machines = [ "admin" ];
              roles.signer.machines = [ "signer" ];
            };
          };
        };
      };

      defaults =
        { config, ... }:
        {
          environment.systemPackages = [
            config.services.data-mesher.package
          ];

          clan.data-mesher.network.interface = "eth1";
          clan.data-mesher.bootstrapNodes = [
            "[2001:db8:1::1]:7946" # peer1
            "[2001:db8:1::2]:7946" # peer2
          ];

          # speed up for testing
          services.data-mesher.settings = {
            cluster.join_interval = lib.mkForce "2s";
            cluster.push_pull_interval = lib.mkForce "5s";
          };
        };

      nodes = {
        admin.clan.data-mesher.network.tld = "foo";
      };

      # TODO Add better test script.
      testScript = ''

        def resolve(node, success = {}, fail = [], timeout = 60):
          for hostname, ips in success.items():
              for ip in ips:
                  node.wait_until_succeeds(f"getent ahosts {hostname} | grep {ip}", timeout)

          for hostname in fail:
              node.wait_until_fails(f"getent ahosts {hostname}")

        start_all()

        admin.wait_for_unit("data-mesher")
        signer.wait_for_unit("data-mesher")
        peer.wait_for_unit("data-mesher")

        # check dns resolution
        for node in [admin, signer, peer]:
          resolve(node, {
              "admin.foo": ["2001:db8:1::1", "192.168.1.1"],
              "peer.foo": ["2001:db8:1::2", "192.168.1.2"],
              "signer.foo": ["2001:db8:1::3", "192.168.1.3"]
          })
      '';
    }
  );
}
