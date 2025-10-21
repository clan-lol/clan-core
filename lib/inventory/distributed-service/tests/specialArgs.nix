{ callInventoryAdapter, lib, ... }:
let
  res = callInventoryAdapter {
    modules."A" = m: {
      _class = "clan.service";
      config = {
        manifest = {
          name = "network";
        };
        roles.default = { };

      };
      options.test = lib.mkOption {
        default = m;
      };
    };
    machines = {
      jon = { };
    };
    instances."instance_foo" = {
      module = {
        name = "A";
        input = "self";
      };
      roles.peer.machines.jon = { };
    };
  };

  specialArgs = lib.attrNames res.servicesEval.config.mappedServices.self-A.test.specialArgs;
in
{
  test_simple = {
    expr = specialArgs;
    expected = [
      "clanLib"
      "directory"
      "exports"
    ];
  };
}
