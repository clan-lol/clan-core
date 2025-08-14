# Wraps all services in one fixed point module
{
  # TODO: consume directly from clan.config
  directory,
}:
{
  lib,
  config,
  specialArgs,
  _ctx,
  ...
}:
let
  inherit (lib) mkOption types;
  inherit (types) attrsWith submoduleWith;
in
{
  # TODO: merge these options into clan options
  options = {
    exportsModule = mkOption {
      type = types.deferredModule;
      readOnly = true;
    };
    mappedServices = mkOption {
      visible = false;
      type = attrsWith {
        placeholder = "mappedServiceName";
        elemType = submoduleWith {
          class = "clan.service";
          modules = [
            (
              { name, ... }:
              {
                _module.args._ctx = [ name ];
                _module.args.exports = config.exports;
                _module.args.directory = directory;

              }
            )
            ./service-module.nix
            #  feature modules
            (lib.modules.importApply ./api-feature.nix {
              inherit (specialArgs) clanLib;
              prefix = _ctx;
            })
          ];
        };
      };
      default = { };
    };
    exports = mkOption {
      type = submoduleWith {
        modules = [
          {
            options = {
              instances = lib.mkOption {
                default = { };
                # instances.<instanceName>...
                type = types.attrsOf (submoduleWith {
                  modules = [
                    config.exportsModule
                  ];
                });
              };
              # instances.<machineName>...
              machines = lib.mkOption {
                default = { };
                type = types.attrsOf (submoduleWith {
                  modules = [
                    config.exportsModule
                  ];
                });
              };
            };
          }
        ]
        ++ lib.mapAttrsToList (_: service: service.exports) config.mappedServices;
      };
      default = { };
    };
  };
}
