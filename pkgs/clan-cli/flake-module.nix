{ inputs, ... }:
{
  perSystem = { self', pkgs, ... }: {
    devShells.clan-cli = pkgs.callPackage ./shell.nix {
      inherit (self'.packages) clan-cli-unwrapped ui-assets nix-unit;
    };
    packages = {
      clan-cli-unwrapped = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (self'.packages) ui-assets;
        inherit (inputs) nixpkgs;
      };
      # Don't leak python packages into a devshell.
      # It can be very confusing if you `nix run` than than load the cli from the devshell instead.
      clan-cli = pkgs.runCommand "clan" { } ''
        mkdir $out
        ln -s ${self'.packages.clan-cli-unwrapped}/bin $out
      '';
      inherit (self'.packages.clan-cli-unwrapped) clan-openapi;
      default = self'.packages.clan-cli;
    };

    checks = self'.packages.clan-cli-unwrapped.tests;
  };

}
