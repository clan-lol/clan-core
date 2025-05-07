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
        inventory = {
          modules."@clan/admin" = import ../../clanServices/admin/default.nix;

          machines.client = { };
          machines.server = { };

          instances = {
            ssh-test-one = {
              module.name = "@clan/admin";
              roles.default.machines."server".settings = {
                allowedKeys = {testkey = public-key;};
              };
            };
          };
        };
      };

      nodes = {
        client.environment.etc.private-test-key.source = ./private-test-key;
      };

      testScript = ''
        start_all()

        # Show all addresses
        machines = [client, server]
        for m in machines:
            m.systemctl("start network-online.target")

        for m in machines:
            m.wait_for_unit("network-online.target")

        client.succeed(f"&>2")
        client.succeed(f"ssh -F /dev/null -i /etc/private-test-key -o BatchMode=yes root@server true &>/dev/null")
      '';
    }
  );
}
