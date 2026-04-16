{ config, ... }:
let
  # Adjust, to match the partition's priority.
  rootPartition = "${config.disko.devices.disk."main".device}-part3";
in
{
  boot.loader.grub = {
    efiInstallAsRemovable = true;
    efiSupport = true;
  };

  disko.devices = {
    disk = {
      "main" = {
        name = "main-{{uuid}}";
        device = "{{mainDisk}}";
        type = "disk";
        content = {
          type = "gpt";
          partitions = {
            "boot" = {
              size = "1M";
              type = "EF02"; # for grub MBR
              priority = 1;
            };
            "ESP" = {
              type = "EF00";
              size = "500M";
              priority = 2;
              content = {
                type = "filesystem";
                format = "vfat";
                mountpoint = "/boot";
                mountOptions = [ "umask=0077" ];
              };
            };
            "root" = {
              size = "100%";
              priority = 3;
              content = {
                type = "btrfs";
                extraArgs = [
                  "--force"
                  "--label root"
                ];
                subvolumes = {
                  "@root" = {
                    mountpoint = "/";
                    mountOptions = [ ];
                  };
                  "@nix" = {
                    mountpoint = "/nix";
                    mountOptions = [
                      "compress=zstd"
                      "noatime"
                    ];
                  };
                  "@home" = {
                    mountpoint = "/home";
                    mountOptions = [ "compress=zstd" ];
                  };
                  "@persist" = {
                    mountpoint = "/persist";
                    mountOptions = [ "compress=zstd" ];
                  };
                };
              };
            };
            #"swap" = {
            #  size = "8G"; # adjust
            #  content = {
            #    type = "swap";
            #    discardPolicy = "both";
            #  };
            #};
          };
        };
      };
    };
  };

  fileSystems."/persist".neededForBoot = true;

  # https://www.notashelf.dev/posts/impermanence/#impermanence
  boot.initrd.systemd = {
    enable = true;
    services.rollback = {
      description = "Rollback BTRFS root drive to a pristine state";

      wantedBy = [ "initrd.target" ];
      after = [ "initrd-root-device.target" ];
      before = [ "sysroot.mount" ];

      unitConfig.DefaultDependencies = "no";
      serviceConfig.Type = "oneshot";
      script = ''
        echo "Mounting root btrfs drive..."
        mkdir --parents /mnt
        mount --options "subvol=/" ${rootPartition} /mnt

        if [[ -e /mnt/@root ]]; then
            mkdir --parents /mnt/root.old.d
            timestamp=$(date --date="@$(stat --format=%Y /mnt/@root)" "+%Y-%m-%dT%H:%M:%S")
            echo "Moving @root to 'root.old.d/$timestamp'..."
            mv /mnt/@root "/mnt/root.old.d/$timestamp"
        fi

        delete_subvolume_recursively() {
            IFS=$'\n'
            for subvolume in $(btrfs subvolume list -o "$1" | cut --fields 9- --delimiter ' '); do
                delete_subvolume_recursively "/mnt/$subvolume"
            done
            echo "Deleting subvolume '$subvolume'..."
            btrfs subvolume delete "$1"
        }
        echo "Deleting very old subvolumes..."
        for subvolume in $(find /mnt/root.old.d/ -maxdepth 1 -mtime +30); do
            delete_subvolume_recursively "$subvolume"
        done

        echo "Creating new empty subvolume @root..."
        btrfs subvolume create /mnt/@root

        echo "Finished successfully. Unmounting..."
        umount /mnt
      '';
    };
  };

  # Automatic local snapshots
  # https://digint.ch/btrbk/doc/readme.html
  #$ systemctl start btrbk-<instance>
  services.btrbk = {
    instances."nix" = {
      onCalendar = "0/2:00";
      settings = {
        subvolume = "/nix";
        snapshot_create = "onchange";
        snapshot_dir = "/nix";
        snapshot_preserve = "16h 7d 2w";
        snapshot_preserve_min = "3d";
      };
    };
    instances."home" = {
      onCalendar = "0/2:00";
      settings = {
        subvolume = "/home";
        snapshot_create = "onchange";
        snapshot_dir = "/home";
        snapshot_preserve = "16h 7d 3w 2m";
        snapshot_preserve_min = "3d";
      };
    };
    instances."persist" = {
      onCalendar = "0/2:00";
      settings = {
        subvolume = "/persist";
        snapshot_dir = "/persist";
        snapshot_preserve = "16h 7d 3w 2m";
        snapshot_preserve_min = "3d";
      };
    };
  };
}
