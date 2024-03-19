{ config, lib, ... }:
{
  config = lib.mkIf (config.clanCore.secretStore == "vm") {
    clanCore.secretsDirectory = "/etc/secrets";
    clanCore.secretsUploadDirectory = "/etc/secrets";
    system.clan.secretsModule = "clan_cli.secrets.modules.vm";
    system.clan.factsModule = "clan_cli.facts.modules.vm";
  };
}
