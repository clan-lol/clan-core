{ config, lib, ... }:
{
  config = lib.mkIf (config.clan.core.facts.secretStore == "vm") {
    clan.core.facts.secretPathFunction = secret: "/etc/secrets/${secret.config.name}";
    clan.core.facts.secretUploadDirectory = "/etc/secrets";
    clan.core.facts.secretModule = "clan_cli.facts.secret_modules.vm";
  };
}
