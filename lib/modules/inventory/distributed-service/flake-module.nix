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
      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.<attrName>
      legacyPackages.evalTests-distributedServices = import ./tests {
        inherit lib;
        clanLib = self.clanLib;
      };
      legacyPackages.eval-tests-resolve-module = import ./test-resolve-module.nix {
        inherit lib;
      };

      checks = {
        eval-lib-distributedServices = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${self}#legacyPackages.${system}.evalTests-distributedServices

          touch $out
        '';
        eval-tests-resolve-module = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"
          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${self}#legacyPackages.${system}.eval-tests-resolve-module

          touch $out
        '';
      };
    };
}
