{ inputs, ... }:
{
  perSystem = { self', pkgs, system, ... }: {
    devShells.clan-cli = pkgs.callPackage ./shell.nix {
      inherit (self'.packages) clan-cli ui-assets nix-unit;
    };
    packages = {
      clan-cli = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (self'.packages) ui-assets;
        inherit (inputs) nixpkgs;
        deal = inputs.luispkgs.legacyPackages.${system}.python3Packages.deal;
      };
      inherit (self'.packages.clan-cli) clan-openapi;
      default = self'.packages.clan-cli;
    };

    checks = self'.packages.clan-cli.tests;
  };

}
