test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  inherit (lib)
    mkOption
    flip
    mapAttrs
    types
    ;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest (
  { config, ... }:
  let
    clanFlakeResult = config.clan;
  in
  {
    imports = [ test ];
    options = {
      clanSettings = mkOption {
        default = { };
        type = types.submodule {
          options = {
            clan-core = mkOption { default = self; };
            self = mkOption {
              default = throw ''
                Clan testing: 'clanSettings.self' is required to be set explizitly during testing.

                It is recommended to set 'clanSettings.self' during testing to the directory where the test lives in i.e. './.'
              '';
            };
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
              self
              nixpkgs
              nix-darwin
              ;
          };
          modules = [
            self.clanLib.buildClanModule.flakePartsModule
          ];
        };
      };
    };
    config = {
      nodes = flip mapAttrs clanFlakeResult.clanInternals.inventoryClass.machines (
        machineName: attrs: {
          imports = attrs.machineImports ++ [ self.nixosModules.clanCore ];
          clan.core.settings.directory = "${config.clan.directory}";
          clan.core.settings.machine.name = machineName;
        }
      );
      hostPkgs = pkgs;
      # speed-up evaluation
      defaults = (
        { config, ... }:
        {
          imports = [
            ./minify.nix
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

      _module.args = { inherit self; };
      # to accept external dependencies such as disko
      node.specialArgs.self = self;
    };
  }
))
# .config.result
