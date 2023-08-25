{ self, ... }:
{
  perSystem = { pkgs, system, ... }:
    let
      inherit (self.inputs) floco;
      base = pkgs.callPackage ./default.nix { inherit floco system; clanPkgs = self.packages.${system}; };
    in
    {
      packages = {
        ui = base.pkg.global;
      };
      devShells.ui = pkgs.callPackage ./shell.nix {
        inherit pkgs;
        inherit (base) fmod pkg;
        clanPkgs = self.packages.${system};
      };
    };
}
