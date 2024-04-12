{ inputs, ... }:
{
  perSystem =
    { self', pkgs, ... }:
    {
      devShells.docs = pkgs.callPackage ./shell.nix { inherit (self'.packages) docs; };
      packages = {
        docs = pkgs.python3.pkgs.callPackage ./default.nix { inherit (inputs) nixpkgs; };
      };
    };
}
