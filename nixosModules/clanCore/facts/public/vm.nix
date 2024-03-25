{ config, lib, ... }:
{
  config = lib.mkIf (config.clanCore.facts.publicStore == "vm") {
    clanCore.facts.publicModule = "clan_cli.facts.public_modules.vm";
  };
}
