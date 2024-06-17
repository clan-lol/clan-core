{ config, lib, ... }:
{
  config = lib.mkIf (config.clan.core.facts.publicStore == "vm") {
    clan.core.facts.publicModule = "clan_cli.facts.public_modules.vm";
  };
}
