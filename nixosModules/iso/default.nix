{
  config,
  extendModules,
  lib,
  pkgs,
  ...
}:
let
  # Generates a fileSystems entry for bind mounting a given state folder path
  # It binds directories from /var/clanstate/{some-path} to /{some-path}.
  # As a result, all state paths will be persisted across reboots, because
  #   the state folder is mounted from the host system.
  mkBindMount = path: {
    name = path;
    value = {
      device = "/var/clanstate/${path}";
      options = [ "bind" ];
    };
  };

  # Flatten the list of state folders into a single list
  stateFolders = lib.flatten (
    lib.mapAttrsToList (_item: attrs: attrs.folders) config.clan.core.state
  );

  # A module setting up bind mounts for all state folders
  stateMounts = {
    fileSystems = lib.listToAttrs (map mkBindMount stateFolders);
  };

  isoModule =
    { config, ... }:
    {
      imports = [ stateMounts ];
      options.clan.iso.disko = lib.mkOption {
        type = lib.types.submodule { freeformType = (pkgs.formats.json { }).type; };
        default = {
          disk = {
            iso = {
              type = "disk";
              imageSize = "10G"; # TODO add auto image size in disko
              content = {
                type = "gpt";
                partitions = {
                  boot = {
                    size = "1M";
                    type = "EF02"; # for grub MBR
                    priority = 1; # Needs to be first partition
                  };
                  ESP = {
                    size = "100M";
                    type = "EF00";
                    content = {
                      type = "filesystem";
                      format = "vfat";
                      mountpoint = "/boot";
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
      config = {
        disko.devices = lib.mkOverride 51 config.clan.iso.disko;
        boot.loader.grub.enable = true;
        boot.loader.grub.efiSupport = true;
        boot.loader.grub.device = lib.mkForce "/dev/vda";
        boot.loader.grub.efiInstallAsRemovable = true;
      };
    };

  isoConfig = extendModules { modules = [ isoModule ]; };
in
{
  config = {
    # for clan vm create
    system.clan.iso = isoConfig.config.system.build.diskoImages;
  };
}
