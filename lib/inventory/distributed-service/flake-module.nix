{ self, inputs, ... }:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  perSystem =
    {
      pkgs,
      lib,
      system,
      ...
    }:
    let
      # Common filtered source for inventory tests
      inventoryTestsSrc = lib.fileset.toSource {
        root = ../../..;
        fileset = lib.fileset.unions [
          ../../../flake.nix
          ../../../flake.lock
          (lib.fileset.fileFilter (file: file.name == "flake-module.nix") ../../..)
          ../../../flakeModules
          ../../../lib
          ../../../nixosModules/clanCore
          ../../../nixosModules/machineModules
          ../../../machines
          ../../../inventory.json
          ../../../modules
        ];
      };
    in
    {
      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.<attrName>
      legacyPackages.evalTests-distributedServices = import ./tests {
        inherit lib;
        clanLib = self.clanLib;
      };

      checks = {
        eval-lib-distributedServices = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${inventoryTestsSrc}#legacyPackages.${system}.evalTests-distributedServices

          touch $out
        '';
      };
    };
}
