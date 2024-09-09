{ lib, ... }:

let
  suffix = config.clan.core.machine.diskId;
in
{
  # TO NOT EDIT THIS FILE AFTER INSTALLATION of a machine
  # Otherwise your system might not boot because of missing partitions / filesystems
  boot.loader.grub.efiSupport = lib.mkDefault true;
  boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
  disko.devices = {
    disk = {
      "main" = {
        name = suffix;
        type = "disk";
        # Set the following in flake.nix for each maschine:
        # device = <uuid>;
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
                mountOptions = [ "nofail" ];
              };
            };
            "root" = {
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
