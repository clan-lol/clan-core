{ clanLib, lib, ... }:
let
  eval = lib.evalModules {
    modules = [
      {
        # Trying to write into the default
        options.foo = lib.mkOption {
          type = lib.types.str;
          default = "bar";
        };
        options.protected = lib.mkOption {
          type = lib.types.str;
        };
      }
      {
        # Cannot write into the default set prio
        protected = "protected";
      }
      # Merge the "inventory.json"
      (builtins.fromJSON (builtins.readFile ./1.json))
    ];
  };
in
{
  clanInternals.inventoryClass.inventory = eval.config;
  clanInternals.inventoryClass.introspection = clanLib.introspection.getPrios {
    options = eval.options;
  };
}
