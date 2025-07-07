{ self, inputs, ... }:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  perSystem =
    {
      pkgs,
      system,
      lib,
      ...
    }:
    let
      tests = import ./test.nix { inherit lib; };
    in
    {
      legacyPackages.evalTests-values = tests;
      checks = {
        eval-lib-values = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${
              self.filter {
                name = "lib";
                include = [
                  "flakeModules"
                  "lib"
                ];
              }
            }#legacyPackages.${system}.evalTests-values

          touch $out
        '';
      };
    };
}
