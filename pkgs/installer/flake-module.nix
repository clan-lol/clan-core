{
  self,
  lib,
  ...
}:

let
  flashInstallerModule =
    { config, ... }:

    {
      imports = [
        ./iwd.nix
        self.nixosModules.installer
      ];

      # We don't need state-version in a live installer, we can just set nixos.release directly
      clan.core.settings.state-version.enable = false;
      system.stateVersion = config.system.nixos.release;
      nixpkgs.pkgs = self.inputs.nixpkgs.legacyPackages.x86_64-linux;

      users.users.root.initialHashedPassword = lib.mkForce null;

      boot.loader.grub.efiSupport = lib.mkDefault true;
      boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
      disko.devices = {
        disk = {
          "main" = {
            type = "disk";
            device = lib.mkDefault "/dev/null";
            content = {
              type = "gpt";
              partitions = {
                "boot" = {
                  size = "1M";
                  type = "EF02"; # for grub MBR
                  priority = 1;
                };
                "ESP" = {
                  size = "512M";
                  type = "EF00";
                  content = {
                    type = "filesystem";
                    format = "vfat";
                    mountpoint = "/boot";
                  };
                };
                root = {
                  name = "root";
                  end = "-0";
                  content = {
                    type = "filesystem";
                    format = "f2fs";
                    mountpoint = "/";
                    extraArgs = [
                      "-O"
                      "extra_attr,inode_checksum,sb_checksum,compression"
                    ];
                    # Recommendations for flash: https://wiki.archlinux.org/title/F2FS#Recommended_mount_options
                    mountOptions = [
                      "compress_algorithm=zstd:6,compress_chksum,atgc,gc_merge,lazytime,nodiscard"
                    ];
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
    # $ clan flash write flash-installer --disk main /dev/sdX --yes
    # This will include your ssh public keys in the installer.
    machines.flash-installer = {
      imports = [ flashInstallerModule ];
      boot.loader.grub.enable = lib.mkDefault true;
    };
  };

  flake.checks.x86_64-linux.nixos-test-flash-installer-disk =
    self.nixosConfigurations.flash-installer.config.system.build.installTest;
}
