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
    ./clanTest/flake-module.nix
    ./introspection/flake-module.nix
    ./jsonschema/flake-module.nix
    ./types/flake-module.nix
    ./inventory/flake-module.nix
  ];
  flake.clanLib =
    let
      clanLib = import ./default.nix {
        inherit lib inputs self;
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

      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests-build-clan
      legacyPackages.evalTests-build-clan = import ./tests.nix {
        inherit lib;
        clan-core = self;
      };
      checks = {
        eval-lib-build-clan = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"

          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${
              self.filter {
                include = [
                  "flakeModules"
                  "inventory.json"
                  "lib"
                  "machines"
                  "nixosModules"
                  "modules"
                ];
              }
            }#legacyPackages.${system}.evalTests-build-clan

          touch $out
        '';
      };
    };

}
