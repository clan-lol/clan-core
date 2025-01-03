{ lib, config, ... }:
{
  options.clan.single-disk = {
    device = lib.mkOption {
      default = null;
      type = lib.types.nullOr lib.types.str;
      description = "The primary disk device to install the system on";
    };
  };
  config = {
    warnings = [
      "clanModules.single-disk is deprecated. Please copy the disko config from the module into your machine config."
    ];

    boot.loader.grub.efiSupport = lib.mkDefault true;
    boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
    disko.devices = {
      disk = {
        main = {
          type = "disk";
          # This is set through the UI
          device = config.clan.single-disk.device;

          content = {
            type = "gpt";
            partitions = {
              boot = {
                size = "1M";
                type = "EF02"; # for grub MBR
                priority = 1;
              };
              ESP = {
                size = "512M";
                type = "EF00";
                content = {
                  type = "filesystem";
                  format = "vfat";
                  mountpoint = "/boot";
                  mountOptions = [ "umask=0077" ];
                };
              };
              root = {
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
}
