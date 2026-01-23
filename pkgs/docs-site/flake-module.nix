{
  perSystem =
    {
      pkgs,
      self',
      config,
      ...
    }:
    {
      packages.docs-site = pkgs.callPackage ./default.nix { inherit (self'.packages) docs-markdowns; };

      devShells.docs-site = pkgs.mkShell {
        shellHook = self'.packages.docs-site.preBuild;
        inputsFrom = [ self'.packages.docs-site ];
      };

      checks = config.packages.docs-site.tests;
    };
}
