test:
{ pkgs, self, ... }:
let
  inherit (pkgs) lib;
  inherit (lib) mkOption flip mapAttrs;
  inherit (lib.types) path raw;
  inherit (self.lib.inventory) buildInventory;
  nixos-lib = import (pkgs.path + "/nixos/lib") { };
in
(nixos-lib.runTest (
  { config, ... }:
  let
    serviceConfigs = buildInventory {
      inventory = config.inventory.inventory;
      # TODO: make directory argument optional in buildInventory
      directory = config.inventory.directory;
    };
  in
  {
    imports = [ test ];
    options = {
      inventory.inventory = mkOption {
        description = "Inventory of machines and services";
        type = raw;
      };
      inventory.directory = mkOption {
        description = "Directory which contains the vars";
        type = path;
      };
    };
    config = {
      nodes = flip mapAttrs serviceConfigs.machines (
        machineName: attrs: {
          imports = attrs.machineImports ++ [ self.nixosModules.clanCore ];
          clan.core.settings.directory = "${config.inventory.directory}";
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
