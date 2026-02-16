{
  perSystem =
    {
      pkgs,
      config,
      ...
    }:
    {
      packages.clan-site-assets = pkgs.callPackage ./assets.nix { };
      packages.clan-site = pkgs.callPackage ./default.nix {
        inherit (config.packages) docs-markdowns clan-site-assets;
      };

      devShells.clan-site = pkgs.callPackage ./shell.nix {
        inherit (config.packages) clan-site;
      };

      checks = config.packages.clan-site.tests;
    };
}
