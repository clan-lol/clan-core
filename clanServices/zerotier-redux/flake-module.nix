{
  self,
  lib,
  inputs,
  ...
}:
let
  inputOverrides = builtins.concatStringsSep " " (
    builtins.map (input: " --override-input ${input} ${inputs.${input}}") (builtins.attrNames inputs)
  );

  module = lib.modules.importApply ./default.nix {
    inherit (self) packages;
  };
in
{
  clan.inventory.modules = {
    zerotier-redux = module;
  };
  perSystem =
    { system, pkgs, ... }:
    {
      legacyPackages.eval-tests-zerotier-redux = import ./tests/eval-tests.nix {
        inherit lib module;
        inherit (self) clanLib;
      };
      checks = {
        "eval-tests-zerotier-redux" = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"

          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${self}#legacyPackages.${system}.eval-tests-zerotier-redux

          touch $out
        '';
      };
    };
}
