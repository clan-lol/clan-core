{ config, lib, ... }:
let
  types = lib.types;

  metaOptions = {
    name = lib.mkOption { type = types.str; };
    description = lib.mkOption {
      default = null;
      type = types.nullOr types.str;
    };
    icon = lib.mkOption {
      default = null;
      type = types.nullOr types.str;
    };
  };

  moduleConfig = lib.mkOption {
    default = { };
    type = types.attrsOf types.anything;
  };

  importsOption = lib.mkOption {
    default = [ ];
    type = types.listOf types.str;
  };
in
{
  options = {
    assertions = lib.mkOption {
      type = types.listOf types.unspecified;
      internal = true;
      visible = false;
      default = [ ];
    };
    meta = metaOptions;

    machines = lib.mkOption {
      default = { };
      type = types.attrsOf (
        types.submodule {
          options = {
            inherit (metaOptions) name description icon;
            tags = lib.mkOption {

              default = [ ];
              apply = lib.unique;
              type = types.listOf types.str;
            };
            system = lib.mkOption {
              default = null;
              type = types.nullOr types.str;
            };
            deploy.targetHost = lib.mkOption {
              description = "Configuration for the deployment of the machine";
              default = null;
              type = types.nullOr types.str;
            };
          };
        }
      );
    };

    services = lib.mkOption {
      default = { };
      type = types.attrsOf (
        types.attrsOf (
          types.submodule {
            options.meta = metaOptions;
            options.imports = importsOption;
            options.config = moduleConfig;
            options.machines = lib.mkOption {
              default = { };
              type = types.attrsOf (
                types.submodule {
                  options.imports = importsOption;
                  options.config = moduleConfig;
                }
              );
            };
            options.roles = lib.mkOption {
              default = { };
              type = types.attrsOf (
                types.submodule {
                  options.machines = lib.mkOption {
                    default = [ ];
                    type = types.listOf types.str;
                  };
                  options.tags = lib.mkOption {
                    default = [ ];
                    apply = lib.unique;
                    type = types.listOf types.str;
                  };
                  options.config = moduleConfig;
                  options.imports = importsOption;
                }
              );
            };
          }
        )
      );
    };
  };

  # Smoke validation of the inventory
  config.assertions =
    let
      # Inventory assertions
      # - All referenced machines must exist in the top-level machines
      serviceAssertions = lib.foldlAttrs (
        ass1: serviceName: c:
        ass1
        ++ lib.foldlAttrs (
          ass2: instanceName: instanceConfig:
          let
            serviceMachineNames = lib.attrNames instanceConfig.machines;
            topLevelMachines = lib.attrNames config.machines;
            # All machines must be defined in the top-level machines
            assertions = builtins.map (m: {
              assertion = builtins.elem m topLevelMachines;
              message = "${serviceName}.${instanceName}.machines.${m}. Should be one of [ ${builtins.concatStringsSep " | " topLevelMachines} ]";
            }) serviceMachineNames;
          in
          ass2 ++ assertions
        ) [ ] c
      ) [ ] config.services;

      # Machine assertions
      # - A machine must define their host system
      machineAssertions = map (
        { name, ... }:
        {
          assertion = true;
          message = "Machine ${name} should define its host system in the inventory. ()";
        }
      ) (lib.attrsToList (lib.filterAttrs (_n: v: v.system or null == null) config.machines));
    in
    machineAssertions ++ serviceAssertions;
}
