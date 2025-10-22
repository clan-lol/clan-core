{
  lib,
  clanLib,
  config,
  ...
}:
let
  inherit (lib) types mkOption;
  submodule = m: types.submoduleWith { modules = [ m ]; };

  inspectModule =
    inputName: moduleName: module:
    let
      eval = clanLib.evalService {
        modules = [ module ];
        prefix = [
          inputName
          "clan"
          "modules"
          moduleName
        ];
      };
    in
    {
      manifest = eval.config.manifest;
      roles = lib.mapAttrs (_n: v: { inherit (v) description; }) eval.config.roles;
    };

in
{
  options = {
    flakeInputs = mkOption {
      type = types.raw;
    };
    exportsModule = mkOption {
      type = types.raw;
    };

    distributedServices = mkOption {
      type = types.raw;
    };
    inventory = mkOption {
      type = types.raw;
    };
    directory = mkOption {
      type = types.path;
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

    staticModules = lib.mkOption {
      readOnly = true;
      type = lib.types.raw;

      apply = moduleSet: lib.mapAttrs (inspectModule "<clan-core>") moduleSet;
    };
    modulesPerSource = lib.mkOption {
      # { sourceName :: { moduleName :: {} }}
      readOnly = true;
      type = lib.types.raw;
      default =
        let
          inputsWithModules = lib.filterAttrs (_inputName: v: v ? clan.modules) config.flakeInputs;
        in
        lib.mapAttrs (
          inputName: v: lib.mapAttrs (inspectModule inputName) v.clan.modules
        ) inputsWithModules;
    };
    moduleSchemas = lib.mkOption {
      # { sourceName :: { moduleName :: { roleName :: Schema }}}
      readOnly = true;
      type = lib.types.raw;
      default = lib.mapAttrs (
        _inputName: moduleSet:
        lib.mapAttrs (
          _moduleName: module:
          (clanLib.evalService {
            modules = [ module ];
            prefix = [ ];
          }).config.result.api.schema
        ) moduleSet
      ) config.modulesPerSource;
    };
    templatesPerSource = lib.mkOption {
      # { sourceName :: { moduleName :: {} }}
      readOnly = true;
      type = lib.types.raw;
      default =
        let
          inputsWithTemplates = lib.filterAttrs (_inputName: v: v ? clan.templates) config.flakeInputs;
        in
        lib.mapAttrs (_inputName: v: lib.mapAttrs (_n: t: t) v.clan.templates) inputsWithTemplates;

    };
  };
}
