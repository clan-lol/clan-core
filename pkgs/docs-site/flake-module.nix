{
  perSystem =
    { pkgs, self', ... }:
    {
      packages.docs-site = pkgs.callPackage ./default.nix { inherit (self'.packages) module-docs; };

      devShells.docs-site = pkgs.mkShell {
        shellHook = self'.packages.docs-site.preBuild;
        inputsFrom = [ self'.packages.docs-site ];
      };
    };
}
