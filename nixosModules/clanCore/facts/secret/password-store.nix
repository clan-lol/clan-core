{ config, lib, ... }:
{
  options.clan.password-store.targetDirectory = lib.mkOption {
    type = lib.types.path;
    default = "/etc/secrets";
    description = ''
      The directory where the password store is uploaded to.
    '';
  };

  config = lib.mkIf (config.clan.core.facts.secretStore == "password-store") {
    clan.core.facts.secretPathFunction =
      secret: "${config.clan.password-store.targetDirectory}/${secret.config.name}";
    clan.core.facts.secretUploadDirectory = config.clan.password-store.targetDirectory;
    clan.core.facts.secretModule = "clan_cli.facts.secret_modules.password_store";
  };
}
