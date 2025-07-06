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
  options.localModules = lib.mkOption {
    readOnly = true;
    type = lib.types.raw;
    default = config.modulesPerSource.self;
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
