{
  flakeInputs,
  clanLib,
}:
{ lib, config, ... }:
let
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
      roles = lib.mapAttrs (_n: _v: { }) eval.config.roles;
    };
in
{
  options.staticModules = lib.mkOption {
    readOnly = true;
    type = lib.types.raw;

    apply = moduleSet: lib.mapAttrs (inspectModule "<clan-core>") moduleSet;
  };
  options.modulesPerSource = lib.mkOption {
    # { sourceName :: { moduleName :: {} }}
    readOnly = true;
    type = lib.types.raw;
    default =
      let
        inputsWithModules = lib.filterAttrs (_inputName: v: v ? clan.modules) flakeInputs;
      in
      lib.mapAttrs (
        inputName: v: lib.mapAttrs (inspectModule inputName) v.clan.modules
      ) inputsWithModules;
  };
  options.moduleSchemas = lib.mkOption {
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
  options.templatesPerSource = lib.mkOption {
    # { sourceName :: { moduleName :: {} }}
    readOnly = true;
    type = lib.types.raw;
    default =
      let
        inputsWithTemplates = lib.filterAttrs (_inputName: v: v ? clan.templates) flakeInputs;
      in
      lib.mapAttrs (_inputName: v: lib.mapAttrs (_n: t: t) v.clan.templates) inputsWithTemplates;

  };
}
