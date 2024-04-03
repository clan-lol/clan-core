{ config, ... }:
{
  flake.flakeModules = {
    clan = ./clan.nix;
    default = config.flake.flakeModules.clan;
  };
}
