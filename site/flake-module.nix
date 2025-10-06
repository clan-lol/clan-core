{
  perSystem =
    { pkgs, self', ... }:
    {
      packages.site = pkgs.callPackage ./default.nix { inherit (self'.packages) module-docs; };

      devShells.site = pkgs.mkShell {
        shellHook = self'.packages.site.preBuild;
        inputsFrom = [ self'.packages.site ];
      };
    };
}
