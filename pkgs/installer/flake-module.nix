{ self, lib, ... }:
let
  installerModule =
    { config, pkgs, ... }:
    {
      imports = [
        self.nixosModules.installer
        self.inputs.nixos-generators.nixosModules.all-formats
      ];
      # Provide convenience for connecting to wifi
      networking.wireless.enable = false;

      # Use iwd instead of wpa_supplicant. It has a user friendly CLI
      networking.wireless.iwd = {
        settings = {
          Network = {
            EnableIPv6 = true;
            RoutePriorityOffset = 300;
          };
          Settings = {
            AutoConnect = true;
          };
        };
        enable = true;
      };
      system.stateVersion = config.system.nixos.version;
      nixpkgs.pkgs = self.inputs.nixpkgs.legacyPackages.x86_64-linux;
    };

  installer = lib.nixosSystem {
    modules = [
      installerModule
      { disko.memSize = 4096; } # FIXME: otherwise the image builder goes OOM
    ];
  };
in
{

  clan = {
    clanName = "clan-core";
    directory = self;
    machines.installer = {
      imports = [ installerModule ];
      fileSystems."/".device = lib.mkDefault "/dev/null";
    };
  };
  flake.packages.x86_64-linux.install-iso = installer.config.formats.iso;
  flake.apps.x86_64-linux.install-vm.program = installer.config.formats.vm.outPath;
  flake.apps.x86_64-linux.install-vm-nogui.program = installer.config.formats.vm-nogui.outPath;
}
