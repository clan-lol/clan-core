{ lib, ... }:
{
  perSystem =
    {
      pkgs,
      config,
      system,
      ...
    }:
    let
      clan-site = pkgs.callPackage ./default.nix {
        inherit (config.packages) docs-markdowns clan-site-assets;
      };
    in
    {
      packages = {
        clan-site-assets = pkgs.callPackage ./assets.nix { };
      }
      # We need to support sandboxed nix build for CI. Omit for Darwin because
      # it can't spawn a headless browser, which is needed for rendering
      # mermaid,
      // lib.optionalAttrs (!lib.hasSuffix "darwin" system) {
        inherit clan-site;
      };

      devShells.clan-site = pkgs.callPackage ./shell.nix {
        clan-site = config.packages.clan-site or clan-site;
      };

      # We need to support sandboxed nix build for CI. Omit for Darwin because
      # it can't spawn a headless browser, which is needed for rendering
      # mermaid,
      checks = lib.optionalAttrs (!lib.hasSuffix "darwin" system) config.packages.clan-site.tests;
    };
}
