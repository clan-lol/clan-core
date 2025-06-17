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
in
{
  options = {
    perSystem = mkPerSystemOption (
      { config, pkgs, ... }:
      let
        cfg = config.clan.nixosTests;
      in
      {
        options.clan.nixosTests = mkOption {
          description = "Clan NixOS tests configuration";
          type = types.attrsOf types.unspecified;
          default = { };
        };

        config.checks = lib.optionalAttrs (pkgs.stdenv.isLinux) (
          let
            # Build all individual vars-check derivations
            varsChecks = lib.mapAttrs' (
              name: testModule:
              lib.nameValuePair "vars-check-${name}" (
                let
                  test = nixosLib.runTest (
                    { ... }:
                    {
                      imports = [
                        self.modules.nixosVmTest.clanTest
                        testModule
                      ];
                      
                      hostPkgs = pkgs;
                    }
                  );
                in
                test.config.result.vars-check
              )
            ) cfg;
          in
          lib.mkMerge [
            # Add the VM tests as checks
            (lib.mapAttrs (
              _name: testModule:
              nixosLib.runTest (
                { ... }:
                {
                  imports = [
                    self.modules.nixosVmTest.clanTest
                    testModule
                  ];
                  
                  hostPkgs = pkgs;
                }
              )
            ) cfg)

            # Add a single vars-check that depends on all others XXX if we ever
            # optimize buildbot to perform better with many builds we can
            # remove this and just run the individual vars-checks to speed up
            # parallel evaluation.
            (lib.optionalAttrs (varsChecks != {}) {
              vars-check = pkgs.runCommand "vars-check-all" {
                buildInputs = lib.attrValues varsChecks;
              } ''
                echo "All vars checks passed:"
                ${lib.concatMapStringsSep "\n" (name: "echo '  ✓ ${name}'") (lib.attrNames varsChecks)}
                touch $out
              '';
            })
          ]
        );
      }
    );
  };
}
