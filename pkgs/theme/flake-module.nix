{ self, ... }:
{
  perSystem = { self', pkgs, ... }:
    let
      inherit (self.inputs) floco;
      base = pkgs.callPackage ./default.nix { inherit floco; clanPkgs = self'.packages; };
    in
    {
      packages = {
        theme = base.pkg.global;
      };
      devShells.theme = pkgs.callPackage ./shell.nix {
        inherit pkgs;
        inherit (base) fmod pkg;
        clanPkgs = self'.packages;
      };
    };
}
