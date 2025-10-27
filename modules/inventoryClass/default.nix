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

  exposedInventory = lib.intersectAttrs {
    meta = null;
    machines = null;
    instances = null;
    tags = null;
  } config.inventory;

  filterAttrsRecursive' =
    path: pred: set:
    lib.listToAttrs (
      lib.concatMap (
        name:
        let
          v = set.${name};
          loc = path ++ [ name ];
        in
        if pred loc v then
          [
            (lib.nameValuePair name (if lib.isAttrs v then filterAttrsRecursive' loc pred v else v))
          ]
        else
          [ ]
      ) (lib.attrNames set)
    );

  filteredInventory = filterAttrsRecursive' [ ] (
    # Remove extraModules from serialization,
    # identified by: prefix + pathLength + name
    # inventory.instances.*.roles.*.extraModules
    path: _value: !(lib.length path == 5 && ((lib.last path)) == "extraModules")
  ) exposedInventory;
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
    inventorySerialization = mkOption {
      type = types.raw;
      readOnly = true;
      default = filteredInventory;
    };
    directory = mkOption {
      type = types.path;
    };
    relativeDirectory = mkOption {
      type = types.str;
      internal = true;
      description = ''
        The relative directory path from the flake root to the clan directory.
        Empty string if directory equals the flake root.
      '';
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
