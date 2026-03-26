{
  self,
  lib,
  ...
}:
let
  importFlake =
    flakeDir:
    let
      flakeExpr = import (flakeDir + "/flake.nix");
      inputs = lib.intersectAttrs flakeExpr.inputs self.inputs;
      flake = flakeExpr.outputs (
        inputs
        // {
          self = flake // {
            outPath = flakeDir;
          };
          clan-core = self;
          systems = builtins.toFile "flake.systems.nix" ''[ "x86_64-linux" ]'';
        }
      );
    in
    lib.throwIf (lib.pathExists (
      flakeDir + "/flake.lock"
    )) "nixos-documentation test should not have a flake.lock file" flake;

  testFlake = importFlake ./.;
in
{
  perSystem =
    { pkgs, ... }:
    {
      checks = lib.optionalAttrs pkgs.stdenv.isLinux {
        nixos-documentation = testFlake.nixosConfigurations.test-documentation.config.system.build.toplevel;
      };
    };
}
