{ config, lib, ... }:
{
  config = lib.mkIf (config.clanCore.facts.publicStore == "in_repo") {
    clanCore.facts.publicModule = "clan_cli.facts.public_modules.in_repo";
  };
}
