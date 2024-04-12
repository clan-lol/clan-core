{ inputs, ... }:
{
  perSystem =
    {
      config,
      self',
      pkgs,
      ...
    }:
    {
      devShells.docs = pkgs.callPackage ./shell.nix { inherit (self'.packages) docs; };
      packages = {
        docs = pkgs.python3.pkgs.callPackage ./default.nix { inherit (inputs) nixpkgs; };
        deploy-docs = pkgs.callPackage ./deploy-docs.nix { inherit (config.packages) docs; };
      };
    };
}
