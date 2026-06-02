{
  perSystem =
    { config, lib, ... }:
    {
      # The package is only registered on x86_64-linux (see pkgs/flake-module.nix),
      # so only expose its pytest check where the package exists.
      checks = lib.optionalAttrs (
        config.packages ? clan-release-diff
      ) config.packages.clan-release-diff.tests;
    };
}
