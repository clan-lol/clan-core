{ config, lib, ... }:
{
  config = lib.mkIf (config.clanCore.secretStore == "vm") {
    clanCore.secretsDirectory = "/etc/secrets";
    clanCore.secretsUploadDirectory = "/etc/secrets";
    system.clan.secretFactsModule = "clan_cli.facts.secret_modules.vm";
    system.clan.publicFactsModule = "clan_cli.facts.public_modules.vm";
  };
}
