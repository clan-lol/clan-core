{ clanLib, lib, ... }:
let
  eval = lib.evalModules {
    modules = [
      {
        # Trying to write into the default
        options.foo = lib.mkOption {
          type = lib.types.attrsOf clanLib.types.uniqueDeferredSerializableModule;
        };
      }
      {
        foo = {
          a = { };
          b = { };
        };
      }

      # Merge the "inventory.json"
      (builtins.fromJSON (builtins.readFile ./deferred.json))
    ];
  };
in
{
  clanInternals.inventoryClass.inventory = eval.config;
  clanInternals.inventoryClass.introspection = clanLib.introspection.getPrios {
    options = eval.options;
  };
}
