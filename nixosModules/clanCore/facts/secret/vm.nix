{ config, lib, ... }:
{
  config = lib.mkIf (config.clanCore.facts.secretStore == "vm") {
    clanCore.facts.secretDirectory = "/etc/secrets";
    clanCore.facts.secretUploadDirectory = "/etc/secrets";
    clanCore.facts.secretModule = "clan_cli.facts.secret_modules.vm";
  };
}
