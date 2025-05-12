{
  pkgs,
  self,
  clanLib,
  ...
}:

let
  public-key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAII6zj7ubTg6z/aDwRNwvM/WlQdUocMprQ8E92NWxl6t+ test@test";
in

clanLib.test.makeTestClan {
  inherit pkgs self;
  nixosTest = (
    { ... }:

    {
      name = "admin";

      clan = {
        directory = ./.;
        modules."@clan/admin" = ../../clanServices/admin/default.nix;
        inventory = {

          machines.client = { };
          machines.server = { };

          instances = {
            ssh-test-one = {
              module.name = "@clan/admin";
              roles.default.machines."server".settings = {
                allowedKeys.testkey = public-key;
              };
            };
          };
        };
      };

      nodes = {
        client.environment.etc.private-test-key.source = ./private-test-key;

        server = {
          services.openssh = {
            enable = true;
            settings.UsePAM = false;
          };
        };
      };

      testScript = ''
        start_all()

        machines = [client, server]
        for m in machines:
            m.systemctl("start network-online.target")

        for m in machines:
            m.wait_for_unit("network-online.target")

        client.succeed(f"ssh -F /dev/null -i /etc/private-test-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes root@server true &>/dev/null")
      '';
    }
  );
}
