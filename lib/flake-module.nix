{
  lib,
  inputs,
  self,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
rec {
  # TODO: automatically generate this from the directory conventions
  imports = [
    ./modules/flake-module.nix
    ./clanTest/flake-module.nix
    ./introspection/flake-module.nix
    ./modules/inventory/flake-module.nix
    ./jsonschema/flake-module.nix
    ./types/flake-module.nix
  ];
  flake.clanLib = import ./default.nix {
    inherit lib inputs self;
  };
  # TODO: remove this legacy alias
  flake.lib = flake.clanLib;

  perSystem =
    {
      pkgs,
      lib,
      system,
      ...
    }:
    let
      # Common filtered source for module tests
      inventoryTestsSrc = lib.fileset.toSource {
        root = ../.;
        fileset = lib.fileset.unions [
          ../flake.nix
          ../flake.lock
          ../lib
          (lib.fileset.fileFilter (file: file.name == "flake-module.nix") ../.)
          ../flakeModules
          # ../../nixosModules/clanCore
          # ../../machines
          # ../../inventory.json
        ];
      };
    in
    {
      legacyPackages.eval-tests-resolve-module = import ./resolve-module/test.nix {
        inherit lib;
      };

      checks = {
        eval-lib-resolve-module = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${inventoryTestsSrc}#legacyPackages.${system}.eval-tests-resolve-module

          touch $out
        '';
      };
    };

}
