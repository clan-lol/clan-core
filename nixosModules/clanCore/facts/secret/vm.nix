{ config, lib, ... }:
{
  config = lib.mkIf (config.clanCore.facts.secretStore == "vm") {
    clanCore.facts.secretPathFunction = secret: "/etc/secrets/${secret.config.name}";
    clanCore.facts.secretUploadDirectory = "/etc/secrets";
    clanCore.facts.secretModule = "clan_cli.facts.secret_modules.vm";
  };
}
