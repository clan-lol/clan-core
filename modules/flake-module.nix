{
  self,
  inputs,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  imports = [
    ./clan/flake-module.nix
  ];
  perSystem =
    {
      pkgs,
      lib,
      system,
      ...
    }:
    let
      jsonDocs = import ./eval-docs.nix {
        inherit pkgs lib;
        clan-core = self;
      };
    in
    {
      legacyPackages.clan-options = jsonDocs.optionsJSON;

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
                ];
              }
            }#legacyPackages.${system}.evalTests-build-clan

          touch $out
        '';
      };
    };
}
