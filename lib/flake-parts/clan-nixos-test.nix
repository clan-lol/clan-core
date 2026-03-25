{
  lib,
  flake-parts-lib,
  self,
  inputs,
  ...
}:
let
  inherit (lib)
    mkOption
    types
    ;
  inherit (flake-parts-lib)
    mkPerSystemOption
    ;
  nixosLib = import (inputs.nixpkgs + "/nixos/lib") { };

  crossCompat = import ./clan-cross-compat.nix {
    inherit lib self nixosLib;
    crossPkgs = self.clanTestCrossPkgs;
  };
in
{
  options = {
    perSystem = mkPerSystemOption (
      { config, pkgs, ... }:
      let
        cfg = config.clan.nixosTests;

        # Evaluated tests, shared between checks output and cross-compat check
        tests = lib.mapAttrs (
          _name: testModule:
          nixosLib.runTest (
            { ... }:
            {
              imports = [
                self.modules.nixosTest.clanTest
                testModule
              ];

              hostPkgs = pkgs;

              defaults = {
                imports = [
                  {
                    _module.args.clan-core = self;
                  }
                ];
              };
            }
          )
        ) cfg;
      in
      {
        options.clan.nixosTests = mkOption {
          description = "Unstable interface! Clan NixOS tests configuration";
          type = types.attrsOf types.unspecified;
          default = { };
        };

        config.checks =
          lib.optionalAttrs (pkgs.stdenv.isLinux) tests
          // lib.optionalAttrs (pkgs.stdenv.hostPlatform.system == "x86_64-linux") {
            clan-cross-compat = crossCompat.mkAllChecks pkgs tests cfg;
          };
      }
    );
  };
}
