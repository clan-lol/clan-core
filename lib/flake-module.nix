{
  lib,
  inputs,
  self,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;

  flakeExtension =
    let
      clanLib =
        let
          clanLib = import ./default.nix {
            inherit lib;
          };
        in
        # Extend clanLib here by lib.clan
        # This allows clanLib to stay agnostic from flakes or clan-core
        lib.fix (
          lib.extends (final: _: {
            buildClan =
              module:
              lib.warn ''
                ==================== DEPRECATION NOTICE ====================
                Please migrate
                from: 'clan = inputs.<clan-core>.lib.buildClan'
                to  : 'clan = inputs.<clan-core>.lib.clan'
                in your flake.nix.

                Please also migrate
                from: 'inherit (clan) nixosConfigurations clanInternals; '
                to  : "
                        inherit (clan.config) nixosConfigurations clanInternals;
                        clan = clan.config;
                      "
                in your flake.nix.

                Reason:
                - Improves consistency between flake-parts and non-flake-parts users.

                - It also allows us to use the top level attribute 'clan' to expose
                  attributes that can be used for cross-clan functionality.
                ============================================================
              '' (final.clan module).config;
            clan = import ./clan {
              inherit lib;
              clan-core = self;
            };
          }) clanLib.__unfix__
        );
    in
    {
      # convenience alias
      lib = clanLib;
      inherit clanLib;
    };
in
{
  # TODO: automatically generate this from the directory conventions
  imports = [
    ./clanTest/flake-module.nix
    ./introspection/flake-module.nix
    ./jsonschema/flake-module.nix
    ./types/flake-module.nix
    ./inventory/flake-module.nix
  ];
  flake = flakeExtension;

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
        ];
      };
    in
    {
      legacyPackages.eval-tests-resolve-module = import ./resolve-module/test.nix {
        inherit lib;
      };

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests-build-clan
      legacyPackages.evalTests-build-clan = import ./tests.nix {
        inherit lib;
        clan-core = self;
      };
      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests-exports
      legacyPackages.evalTests-exports = import ./exports/tests.nix {
        inherit lib;
        clan-core = self;
      };

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests-relativeDir
      legacyPackages.evalTests-relativeDir = import ./clanTest/relativeDir-test.nix {
        inherit lib;
      };

      # Run: nix build .#legacyPackages.x86_64-linux.evalCheck-eval-lib-relativeDir
      legacyPackages.evalCheck-eval-lib-relativeDir = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-lib-relativeDir";
        flakeAttr = "${inventoryTestsSrc}#legacyPackages.${system}.evalTests-relativeDir";
      };

      legacyPackages.evalCheck-eval-lib-resolve-module = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-lib-resolve-module";
        flakeAttr = "${inventoryTestsSrc}#legacyPackages.${system}.eval-tests-resolve-module";
      };

      legacyPackages.evalCheck-eval-lib-build-clan = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-lib-build-clan";
        flakeAttr = "${
          self.filter {
            include = [
              "flake.nix"
              "clanServices"
              "flakeModules"
              "inventory.json"
              "lib"
              "machines"
              "nixosModules"
              "darwinModules"
              "modules"
            ];
          }
        }#legacyPackages.${system}.evalTests-build-clan";
      };

      legacyPackages.evalCheck-eval-lib-exports = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-lib-exports";
        flakeAttr = "${
          self.filter {
            include = [
              "flake.nix"
              "flakeModules"
              "inventory.json"
              "lib"
              "machines"
              "nixosModules"
              "modules"
            ];
          }
        }#legacyPackages.${system}.evalTests-exports";
      };
    };

}
