{
  perSystem =
    {
      pkgs,
      self',
      config,
      ...
    }:
    {
      packages.site = pkgs.callPackage ./default.nix { inherit (self'.packages) docs-markdowns; };

      devShells.site = pkgs.mkShell {
        shellHook = self'.packages.site.preBuild;
        inputsFrom = [ self'.packages.site ];
      };

      checks = config.packages.site.tests;
    };
}
