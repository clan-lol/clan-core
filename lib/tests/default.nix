{ lib, clanLib }:
let
  inherit (lib)
    mkOption
    types
    ;
in
{
  minifyModule = ./minify.nix;
  # A function that returns an extension to runTest
  makeTestClan =
    {
      nixosTest,
      pkgs,
      self,
      ...
    }:
    let
      nixos-lib = import (pkgs.path + "/nixos/lib") { };
    in
    (nixos-lib.runTest (
      { config, ... }:
      let
        clanFlakeResult = config.clan;
      in
      {
        imports = [ nixosTest ];
        options = {
          clanSettings = mkOption {
            default = { };
            type = types.submodule {
              options = {
                clan-core = mkOption { default = self; };
                nixpkgs = mkOption { default = self.inputs.nixpkgs; };
                nix-darwin = mkOption { default = self.inputs.nix-darwin; };
              };
            };
          };

          clan = mkOption {
            default = { };
            type = types.submoduleWith {
              specialArgs = {
                inherit (config.clanSettings)
                  clan-core
                  nixpkgs
                  nix-darwin
                  ;
              };
              modules = [
                clanLib.buildClanModule.flakePartsModule
              ];
            };
          };
        };
        config = {
          nodes = clanFlakeResult.clanInternals.nixosModules;
          hostPkgs = pkgs;
          # speed-up evaluation
          defaults = (
            { config, ... }:
            {
              imports = [
                clanLib.test.minifyModule
              ];
              documentation.enable = lib.mkDefault false;
              nix.settings.min-free = 0;
              system.stateVersion = config.system.nixos.release;
              boot.initrd.systemd.enable = false;

              # setup for sops
              sops.age.keyFile = "/run/age-key.txt";
              system.activationScripts =
                {
                  setupSecrets.deps = [ "age-key" ];
                  age-key.text = ''
                    echo AGE-SECRET-KEY-1PL0M9CWRCG3PZ9DXRTTLMCVD57U6JDFE8K7DNVQ35F4JENZ6G3MQ0RQLRV > /run/age-key.txt
                  '';
                }
                // lib.optionalAttrs (lib.filterAttrs (_: v: v.neededForUsers) config.sops.secrets != { }) {
                  setupSecretsForUsers.deps = [ "age-key" ];
                };
            }
          );

          # to accept external dependencies such as disko
          _module.args = { inherit self; };
          node.specialArgs.self = self;
        };
      }
    )).config.result;
}
