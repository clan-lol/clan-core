{ lib, ... }:

let
  suffix = config.clan.core.machine.diskIdShort;
in
{
  # TO NOT EDIT THIS FILE AFTER INSTALLATION of a machine
  # Otherwise your system might not boot because of missing partitions / filesystems
  boot.loader.grub.efiSupport = lib.mkDefault true;
  boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
  disko.devices = {
    disk = {
      main = {
        type = "disk";
        # Set the following in flake.nix for each maschine:
        # device = <uuid>;
        content = {
          type = "gpt";
          partitions = {
            "boot-${suffix}" = {
              size = "1M";
              type = "EF02"; # for grub MBR
              priority = 1;
            };
            "ESP-${suffix}" = {
              size = "512M";
              type = "EF00";
              content = {
                type = "filesystem";
                format = "vfat";
                mountpoint = "/boot";
                mountOptions = [ "nofail" ];
              };
            };
            "root-${suffix}" = {
              size = "100%";
              content = {
                type = "filesystem";
                format = "ext4";
                # format = "btrfs";
                # format = "bcachefs";
                mountpoint = "/";
              };
            };
          };
        };
      };
    };
  };
}
