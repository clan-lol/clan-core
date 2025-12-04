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
          description = "Unstable interface! Clan NixOS tests configuration";
          type = types.attrsOf types.unspecified;
          default = { };
        };

        config.checks = lib.optionalAttrs (pkgs.stdenv.isLinux) (
          # Add the VM tests as checks (vars-check is part of the test closure)
          lib.mapAttrs (
            _name: testModule:
            nixosLib.runTest (
              { ... }:
              {
                imports = [
                  self.modules.nixosTest.clanTest
                  testModule
                ];

                # Extend pkgs with patched systemd for container tests
                hostPkgs = pkgs.extend (
                  _final: _prev: {
                    systemd = config.packages.systemd;
                  }
                );

                defaults = {
                  imports = [
                    {
                      _module.args.clan-core = self;
                    }
                  ];
                };
              }
            )
          ) cfg
        );
      }
    );
  };
}
