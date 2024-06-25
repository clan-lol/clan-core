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
    name = "machineRef";
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
    name = "tagRef";
    description = "Tags :: [${builtins.concatStringsSep " | " allTags}]";
    check = v: lib.isString v && builtins.elem v allTags;
    merge = lib.mergeEqualOption;
  };
in
{
  options.assertions = lib.mkOption {
    type = t.listOf t.unspecified;
    internal = true;
    default = [ ];
  };
  config.assertions = lib.foldlAttrs (
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

  options.meta = metaOptions;

  options.machines = lib.mkOption {
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
        };
      }
    );
  };

  options.services = lib.mkOption {
    default = { };
    type = t.attrsOf (
      t.attrsOf (
        t.submodule {
          options.meta = metaOptions;
          options.config = lib.mkOption {
            default = { };
            type = t.anything;
          };
          options.machines = lib.mkOption {
            default = { };
            type = t.attrsOf (
              t.submodule {
                options.config = lib.mkOption {
                  default = { };
                  type = t.anything;
                };
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
              }
            );
          };
        }
      )
    );
  };
}
