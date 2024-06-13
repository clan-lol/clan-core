{ ... }:
{
  perSystem =
    { self', pkgs, ... }:
    {

      devShells.matrix-bot = pkgs.callPackage ./shell.nix { inherit (self'.packages) matrix-bot; };
      packages = {
        matrix-bot = pkgs.python3.pkgs.callPackage ./default.nix { };
      };

      checks = { };
    };
}
