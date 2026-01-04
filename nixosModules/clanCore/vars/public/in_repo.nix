{ config, lib, ... }:
let
  inherit (lib)
    mkOptionDefault
    mkIf
    readFile
    pathExists
    ;

  storeTypes = {
    "in_repo" = {
      publicModule = "clan_lib.vars.public_modules.in_repo";
      fileModule = (
        file: {
          flakePath = mkIf (file.config.secret == false) (
            if file.config.share then
              (
                config.clan.core.settings.directory
                + "/vars/shared/${file.config.generatorName}/${file.config.name}/value"
              )
            else
              (
                config.clan.core.settings.directory
                + "/vars/per-machine/${config.clan.core.settings.machine.name}/${file.config.generatorName}/${file.config.name}/value"
              )
          );
          value = mkIf (file.config.secret == false) (
            # dynamically adjust priority to allow overriding with mkDefault in case the file is not found
            if file.config.exists then
              # if the file is found it should have normal priority
              readFile file.config.flakePath
            else
              # if the file is not found, we want to downgrade the priority, to allow overriding via mkDefault
              mkOptionDefault (
                throw "Please run `clan vars generate ${config.clan.core.settings.machine.name}` as file was not found: ${file.config.path}"
              )
          );
          exists = mkIf (file.config.secret == false) (pathExists file.config.flakePath);
        }
      );
    };
  };
in
{
  config.clan.core.vars.settings = {
    inherit (storeTypes.${config.clan.core.vars.settings.publicStore}) publicModule fileModule;
  };
}
