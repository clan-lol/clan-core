{ self, inputs, ... }:
let
  inputOverrides = builtins.concatStringsSep " " (
    builtins.map (input: " --override-input ${input} ${inputs.${input}}") (builtins.attrNames inputs)
  );
in
{
  perSystem =
    {
      pkgs,
      lib,
      system,
      ...
    }:
    {
      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests
      legacyPackages.evalTests-select = import ./tests.nix {
        inherit lib;
        inherit (self) clanLib;
      };

      checks = {
        lib-select-eval = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          export NIX_ABORT_ON_WARN=1
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${
              self.filter {
                include = [
                  "flakeModules"
                  "lib"
                  "clanModules/flake-module.nix"
                  "clanModules/borgbackup"
                ];
              }
            }#legacyPackages.${system}.evalTests-select

          touch $out
        '';
      };
    };
}
