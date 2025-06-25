{
  flakeInputs,
  clanLib,
  localModuleSet,
}:
{ lib, config, ... }:

let

  inspectModule =
    inputName: moduleName: module:
    let
      eval = clanLib.inventory.evalClanService {
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
    default =
      let
        inputsWithModules = lib.filterAttrs (_inputName: v: v ? clan.modules) flakeInputs;

      in
      lib.mapAttrs (
        inputName: v: lib.mapAttrs (inspectModule inputName) v.clan.modules
      ) inputsWithModules;
  };
  options.localModules = lib.mkOption {
    default = lib.mapAttrs (inspectModule "self") localModuleSet;
  };
}
