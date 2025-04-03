test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  inherit (lib) mkOption flip mapAttrs;
  inherit (lib.types) raw;
  inherit (self.lib.inventory) buildInventory;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest (
  { config, ... }:
  {
    imports = [ test ];
    options = {
      inventory = mkOption {
        description = "Inventory of machines and services";
        type = raw;
      };
      serviceConfigs = mkOption {
        description = "Result of the evaluated inventory";
        type = raw;
        readOnly = true;
      };
    };
    config = {
      serviceConfigs = buildInventory {
        inventory = config.inventory;
        # TODO: make directory argument optional in buildInventory
        directory = ./.;
      };
      nodes = flip mapAttrs config.serviceConfigs.machines (
        machineName: attrs: {
          imports = attrs.machineImports ++ [ self.nixosModules.clanCore ];
          clan.core.settings.directory = builtins.toString ./.;
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
        }
      );

      _module.args = { inherit self; };
      # to accept external dependencies such as disko
      node.specialArgs.self = self;
    };
  }
)).config.result
