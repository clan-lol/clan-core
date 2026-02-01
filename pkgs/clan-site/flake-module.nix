{
  perSystem =
    {
      pkgs,
      config,
      ...
    }:
    {
      packages.clan-site = pkgs.callPackage ./default.nix {
        inherit (config.packages) docs-markdowns;
      };

      devShells.clan-site = pkgs.callPackage ./shell.nix {
        inherit (config.packages) clan-site;
      };

      checks = config.packages.clan-site.tests;
    };
}
