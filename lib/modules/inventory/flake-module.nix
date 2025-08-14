{
  self,
  inputs,
  options,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  imports = [
    ./distributed-service/flake-module.nix
  ];
  perSystem =
    {
      pkgs,
      lib,
      config,
      system,
      self',
      ...
    }:
    {
      devShells.inventory-schema = pkgs.mkShell {
        name = "clan-inventory-schema";
        inputsFrom = with config.checks; [
          eval-lib-inventory
          self'.devShells.default
        ];
      };

      legacyPackages.schemas = (
        import ./schemas {
          flakeOptions = options;
          inherit
            pkgs
            self
            lib
            self'
            ;
        }
      );

      legacyPackages.clan-service-module-interface =
        (pkgs.nixosOptionsDoc {
          options =
            (self.clanLib.evalService {
              modules = [ { _docs_rendering = true; } ];
              prefix = [ ];
            }).options;
          warningsAreErrors = true;
          transformOptions = self.clanLib.docs.stripStorePathsFromDeclarations;
        }).optionsJSON;

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests
      legacyPackages.evalTests-inventory = import ./tests {
        inherit lib;
        clan-core = self;
        inherit (self) clanLib;
        inherit (self.inputs) nix-darwin;
      };

      checks = {
        eval-lib-inventory = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          export NIX_ABORT_ON_WARN=1
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
                  ../../../flakeModules
                  ../../../lib
                  ../../../nixosModules/clanCore
                  ../../../machines
                  ../../../inventory.json
                ];
              }
            }#legacyPackages.${system}.evalTests-inventory

          touch $out
        '';
      };
    };
}
