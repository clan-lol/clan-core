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
        inherit lib pkgs;
      };
      checks.eval-module-clan-vars = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
        export HOME="$(realpath .)"

        nix-unit --eval-store "$HOME" \
          --extra-experimental-features flakes \
          --show-trace \
          ${inputOverrides} \
          --flake ${
            lib.fileset.toSource {
              root = ../../..;
              fileset = lib.fileset.unions [
                ../../../flake.nix
                ../../../flake.lock
                (lib.fileset.fileFilter (file: file.name == "flake-module.nix") ../../..)
                ../../../flakeModules/clan.nix
                ../../../lib
                ../../../nixosModules/clanCore/vars
              ];
            }
          }#legacyPackages.${system}.evalTests-module-clan-vars

        touch $out
      '';
    };
}
