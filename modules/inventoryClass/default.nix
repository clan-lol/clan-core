{ lib, clanLib, config, ... }:
let
  inherit (lib) types mkOption;
  submodule = m: types.submoduleWith { modules = [ m ]; };
in
{
  options = {
    directory = mkOption {
      type = types.path;
    };
    distributedServices = mkOption {
      type = types.raw;
    };
    inventory = mkOption {
      type = types.raw;
    };
    machines = mkOption {
      type = types.attrsOf (submodule ({
        options = {
          machineImports = mkOption {
            type = types.listOf types.raw;
          };
        };
      }));
    };
    introspection = lib.mkOption {
      readOnly = true;
      # TODO: use options.inventory instead of the evaluate config attribute
      default =
        builtins.removeAttrs (clanLib.introspection.getPrios { options = config.inventory.options; })
          # tags are freeformType which is not supported yet.
          # services is removed and throws an error if accessed.
          [
            "tags"
            "services"
          ];
    };
  };
}
