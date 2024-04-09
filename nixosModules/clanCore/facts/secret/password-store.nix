{ config, lib, ... }:
{
  options.clan.password-store.targetDirectory = lib.mkOption {
    type = lib.types.path;
    default = "/etc/secrets";
    description = ''
      The directory where the password store is uploaded to.
    '';
  };

  config = lib.mkIf (config.clanCore.facts.secretStore == "password-store") {
    clanCore.facts.secretPathFunction = secret: "/etc/secrets/${secret.config.name}";
    clanCore.facts.secretUploadDirectory = config.clan.password-store.targetDirectory;
    clanCore.facts.secretModule = "clan_cli.facts.secret_modules.password_store";
  };
}
