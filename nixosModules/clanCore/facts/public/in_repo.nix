{ config, lib, ... }:
{
  config = lib.mkIf (config.clan.core.facts.publicStore == "in_repo") {
    clan.core.facts.publicModule = "clan_cli.facts.public_modules.in_repo";
  };
}
