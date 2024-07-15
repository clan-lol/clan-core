{ config, lib, ... }:
let
  t = lib.types;

  metaOptions = {
    name = lib.mkOption { type = t.str; };
    description = lib.mkOption {
      default = null;
      type = t.nullOr t.str;
    };
    icon = lib.mkOption {
      default = null;
      type = t.nullOr t.str;
    };
  };

  machineRef = lib.mkOptionType {
    name = "str";
    description = "Machine :: [${builtins.concatStringsSep " | " (builtins.attrNames config.machines)}]";
    check = v: lib.isString v && builtins.elem v (builtins.attrNames config.machines);
    merge = lib.mergeEqualOption;
  };

  allTags = lib.unique (
    lib.foldlAttrs (
      tags: _: m:
      tags ++ m.tags or [ ]
    ) [ ] config.machines
  );

  tagRef = lib.mkOptionType {
    name = "str";
    description = "Tags :: [${builtins.concatStringsSep " | " allTags}]";
    check = v: lib.isString v && builtins.elem v allTags;
    merge = lib.mergeEqualOption;
  };

  moduleConfig = lib.mkOption {
    default = { };
    type = t.attrsOf t.anything;
  };

  importsOption = lib.mkOption {
    default = [ ];
    type = t.listOf t.str;
  };
in
{
  options = {
    assertions = lib.mkOption {
      type = t.listOf t.unspecified;
      internal = true;
      visible = false;
      default = [ ];
    };
    meta = metaOptions;

    machines = lib.mkOption {
      default = { };
      type = t.attrsOf (
        t.submodule {
          options = {
            inherit (metaOptions) name description icon;
            tags = lib.mkOption {
              default = [ ];
              apply = lib.unique;
              type = t.listOf t.str;
            };
            system = lib.mkOption {
              default = null;
              type = t.nullOr t.str;
            };
          };
        }
      );
    };

    services = lib.mkOption {
      default = { };
      type = t.attrsOf (
        t.attrsOf (
          t.submodule {
            options.meta = metaOptions;
            options.imports = importsOption;
            options.config = moduleConfig;
            options.machines = lib.mkOption {
              default = { };
              type = t.attrsOf (
                t.submodule {
                  options.imports = importsOption;
                  options.config = moduleConfig;
                }
              );
            };
            options.roles = lib.mkOption {
              default = { };
              type = t.attrsOf (
                t.submodule {
                  options.machines = lib.mkOption {
                    default = [ ];
                    type = t.listOf machineRef;
                  };
                  options.tags = lib.mkOption {
                    default = [ ];
                    apply = lib.unique;
                    type = t.listOf tagRef;
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
