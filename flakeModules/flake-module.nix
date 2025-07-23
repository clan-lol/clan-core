{
  self,
  inputs,
  config,
  lib,
  flake-parts-lib,
  ...
}:
{
  flake.flakeModules = {
    clan = import ./clan.nix self;
    default = config.flake.flakeModules.clan;
    testModule = import ../lib/flake-parts/clan-nixos-test.nix {
      inherit
        self
        inputs
        lib
        flake-parts-lib
        ;
    };
  };
}
