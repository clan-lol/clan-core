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
    clan = import ./clan.nix {
      clan-core = self;
      inherit flake-parts-lib;
    };
    default = config.flake.flakeModules.clan;
    # testModule is an unstable interface and can change at any time.
    testModule = lib.modules.importApply ../lib/flake-parts/clan-nixos-test.nix {
      inherit
        self
        inputs
        lib
        flake-parts-lib
        ;
    };
  };
}
