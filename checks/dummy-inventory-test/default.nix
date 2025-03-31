(import ../lib/test-inventory.nix) (
  { ... }:
  {
    name = "dummy-inventory-test";

    inventory = {
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
      admin1.wait_for_unit("dummy-service")
      peer1.wait_for_unit("dummy-service")
    '';
  }
)
