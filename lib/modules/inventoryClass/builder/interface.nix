{ lib, ... }:
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
  };
}
