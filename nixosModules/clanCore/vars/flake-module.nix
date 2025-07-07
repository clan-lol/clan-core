{
  self,
  inputs,
  lib,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  perSystem =
    { system, pkgs, ... }:
    {
      legacyPackages.evalTests-module-clan-vars = import ./eval-tests {
        inherit lib;
        clan-core = self;
        pkgs = inputs.nixpkgs.legacyPackages.${system};
      };
      checks.eval-module-clan-vars = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
        export HOME="$(realpath .)"

        nix-unit --eval-store "$HOME" \
          --extra-experimental-features flakes \
          --show-trace \
          ${inputOverrides} \
          --flake ${
            self.filter {
              include = [
                "flakeModules"
                "nixosModules"
                "lib"
              ];
            }
          }#legacyPackages.${system}.evalTests-module-clan-vars

        touch $out
      '';
    };
}
