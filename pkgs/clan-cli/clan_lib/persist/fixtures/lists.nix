{ clanLib, lib, ... }:
let
  eval = lib.evalModules {
    modules = [
      {
        # Trying to write into the default
        options.empty = lib.mkOption {
          type = lib.types.listOf lib.types.str;
        };
        options.predefined = lib.mkOption {
          type = lib.types.listOf lib.types.str;
        };
      }
      {
        empty = [ ];
        predefined = [
          "a"
          "b"
        ];
      }

      # Merge the "inventory.json"
      (builtins.fromJSON (builtins.readFile ./lists.json))
    ];
  };
in
{
  clanInternals.inventoryClass.inventorySerialization = eval.config;
  clanInternals.inventoryClass.introspection = clanLib.introspection.getPrios {
    options = eval.options;
  };
}
