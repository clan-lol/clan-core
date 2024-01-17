{ config, lib, ... }:
{
  options.clan.password-store.targetDirectory = lib.mkOption {
    type = lib.types.path;
    default = "/etc/secrets";
    description = ''
      The directory where the password store is uploaded to.
    '';
  };
  config = lib.mkIf (config.clanCore.secretStore == "password-store") {
    clanCore.secretsDirectory = config.clan.password-store.targetDirectory;
    clanCore.secretsUploadDirectory = config.clan.password-store.targetDirectory;
    system.clan.secretsModule = "clan_cli.secrets.modules.password_store";
  };
}

