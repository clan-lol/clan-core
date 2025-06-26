{ self, config, ... }:
{
  flake.flakeModules = {
    clan = import ./clan.nix self.module.clan.default;
    default = config.flake.flakeModules.clan;
  };
}
