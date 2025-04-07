(import ../lib/test-inventory.nix) (
  { ... }:
  {
    name = "dummy-inventory-test";

    inventory.directory = ./.;
    inventory.inventory = {
      machines.peer1 = { };
      machines.admin1 = { };
      services = {
        dummy-module.default = {
          roles.peer.machines = [ "peer1" ];
          roles.admin.machines = [ "admin1" ];
        };
      };
      modules = {
        dummy-module = ./dummy-module;
      };
    };

    testScript = ''
      start_all()
      admin1.wait_for_unit("multi-user.target")
      peer1.wait_for_unit("multi-user.target")
      print(admin1.succeed("systemctl status dummy-service"))
      print(peer1.succeed("systemctl status dummy-service"))
    '';
  }
)
