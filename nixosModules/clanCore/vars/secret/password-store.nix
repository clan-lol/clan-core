{ config, lib, ... }:
{
  config.clan.core.vars.settings =
    lib.mkIf (config.clan.core.vars.settings.secretStore == "password-store")
      {
        fileModule = file: {
          path = lib.mkIf file.secret "${config.clan.core.password-store.targetDirectory}/${config.clan.core.machineName}-${file.config.generatorName}-${file.config.name}";
        };
        secretUploadDirectory = lib.mkDefault "/etc/secrets";
        secretModule = "clan_cli.vars.secret_modules.password_store";
      };
}
