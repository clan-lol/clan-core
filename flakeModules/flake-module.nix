{ self, config, ... }:
{
  flake.flakeModules = {
    clan = import ./clan.nix self;
    default = config.flake.flakeModules.clan;
  };
}
