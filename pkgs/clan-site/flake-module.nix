{
  perSystem =
    {
      pkgs,
      self',
      config,
      ...
    }:
    {
      packages.clan-site = pkgs.callPackage ./default.nix { inherit (self'.packages) docs-markdowns; };

      devShells.clan-site = pkgs.mkShell {
        shellHook = self'.packages.clan-site.preBuild;
        inputsFrom = [ self'.packages.clan-site ];
      };

      checks = config.packages.clan-site.tests;
    };
}
