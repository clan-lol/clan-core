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
            ) cfg)

            varsChecks
          ]
        );
      }
    );
  };
}
