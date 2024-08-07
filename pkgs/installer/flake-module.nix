{ self, lib, ... }:

let
  wifiModule =
    { ... }:
    {
      # use iwd instead of wpa_supplicant
      networking.wireless.enable = false;

      # Use iwd instead of wpa_supplicant. It has a user friendly CLI
      networking.wireless.iwd = {
        enable = true;
        settings = {
          Network = {
            EnableIPv6 = true;
            RoutePriorityOffset = 300;
          };
          Settings.AutoConnect = true;
        };
      };
    };

  flashInstallerModule =
    { config, ... }:
    {
      imports = [
        wifiModule
        self.nixosModules.installer
      ];
      system.stateVersion = config.system.nixos.version;
      nixpkgs.pkgs = self.inputs.nixpkgs.legacyPackages.x86_64-linux;
    }
    // flashDiskoConfig;

  # Important: The partition names need to be different to the clan install
  flashDiskoConfig = {
    boot.loader.grub.efiSupport = lib.mkDefault true;
    boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
    disko.devices = {
      disk = {
        main = {
          type = "disk";
          device = lib.mkDefault "/dev/null";
          content = {
            type = "gpt";
            partitions = {
              installer-boot = {
                size = "1M";
                type = "EF02"; # for grub MBR
                priority = 1;
              };
              installer-ESP = {
                size = "512M";
                type = "EF00";
                content = {
                  type = "filesystem";
                  format = "vfat";
                  mountpoint = "/boot";
                };
              };
              installer-root = {
                size = "100%";
                content = {
                  type = "filesystem";
                  format = "ext4";
                  mountpoint = "/";
                };
              };
            };
          };
        };
      };
    };
  };
in
{
  clan = {
    # To directly flash the installer to a disk, use the following command:
    # $ clan flash flash-installer --disk main /dev/sdX --yes
    # This will include your ssh public keys in the installer.
    machines.flash-installer = {
      imports = [ flashInstallerModule ];
      boot.loader.grub.enable = lib.mkDefault true;
    };
  };
}
