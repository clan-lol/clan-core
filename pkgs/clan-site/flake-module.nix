{ lib, ... }:
{
  perSystem =
    {
      pkgs,
      config,
      system,
      ...
    }:
    {
      packages = {
        clan-site-assets = pkgs.callPackage ./nix/assets.nix { };
        clan-site-cli = pkgs.callPackage ./nix/cli.nix { };
        clan-site = pkgs.callPackage ./nix/clan-site.nix {
          inherit (config.packages)
            clan-site-assets
            clan-site-cli
            docs-source
            ;
        };
      };

      devShells.clan-site = pkgs.callPackage ./nix/shell.nix {
        inherit (config.packages) clan-site clan-site-cli;
      };

      checks = lib.optionalAttrs (!lib.hasSuffix "darwin" system) config.packages.clan-site.tests;
    };
}
