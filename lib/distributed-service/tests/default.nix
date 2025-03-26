{
  lib,
  ...
}:
let
  inherit (lib)
    evalModules
    mkOption
    types
    ;

  inherit (types)
    submodule
    attrsOf
    str
    ;

  evalInventory =
    m:
    (evalModules {
      # Static modules
      modules = [
        ../../inventory/build-inventory/interface.nix
        {
          modules.test = {};
        }
        m
      ];
    }).config;

  flakeFixture = { inputs = {}; };

  callInventoryAdapter = inventoryModule: import ../inventory-adapter.nix { inherit lib; flake = flakeFixture; inventory = evalInventory inventoryModule; };
in
{
  test_simple =
    let res = callInventoryAdapter {
      # Authored module
      # A minimal module looks like this
      # It isn't exactly doing anything but it's a valid module that produces an output
      modules."simple-module" = {
        _class = "clan.service";
        manifest = {
          name = "netwitness";
        };
      };
      # User config
      instances."instance_foo" = {
        module = {
          name = "simple-module";
        };
      };
    };
    in
  {
    # Test that the module is mapped into the output
    # We might change the attribute name in the future
    expr = res.evals ? "self-simple-module";
    expected = true;
  };
}
