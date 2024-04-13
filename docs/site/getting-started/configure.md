# Configuration - How to configure clan with your own machines

## Global configuration

In the `flake.nix` file:

- [x] set a unique `clanName`.
- [ ] set `clanIcon` (optional)
- [ ] Set `machineIcon` per machine (optional)

These icons will be used by our future GUI.

```nix title="clan-core.lib.buildClan"
buildClan {
    # Set a unique name 
    clanName = "Lobsters";
    # Optional, a path to an image file
    clanIcon = ./path/to/file; 

    machines = {
        jon = {
            # ...
            # Optional, a path to an image file
            clanCore.machineIcon = ./path/to/file; 
        };
        # ...
    }
}
```

## Machine configuration

Adding or configuring a new machine requires two simple steps:

### Step 1. Identify Target Disk-ID

1. Find the remote disk id by executing:

    ```bash title="setup computer"
    ssh root@<target-computer> lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
    ```

    Which should show something like:

    ```bash
    NAME        ID-LINK                                         FSTYPE   SIZE MOUNTPOINT
    sda         usb-ST_16GB_AA6271026J1000000509-0:0                    14.9G 
    ├─sda1      usb-ST_16GB_AA6271026J1000000509-0:0-part1                 1M 
    ├─sda2      usb-ST_16GB_AA6271026J1000000509-0:0-part2      vfat     100M /boot
    └─sda3      usb-ST_16GB_AA6271026J1000000509-0:0-part3      ext4     2.9G /
    nvme0n1     nvme-eui.e8238fa6bf530001001b448b4aec2929              476.9G 
    ├─nvme0n1p1 nvme-eui.e8238fa6bf530001001b448b4aec2929-part1 vfat     512M 
    ├─nvme0n1p2 nvme-eui.e8238fa6bf530001001b448b4aec2929-part2 ext4   459.6G 
    └─nvme0n1p3 nvme-eui.e8238fa6bf530001001b448b4aec2929-part3 swap    16.8G
    ```

2. Edit the following fields inside the `flake.nix`

    ```nix title="clan-core.lib.buildClan"
    buildClan {
      # ...
      machines = {
        "jon" = {
          # ...

          # Change this to the correct ip-address or hostname
          # The hostname is the machine name by default
          clan.networking.targetHost = pkgs.lib.mkDefault "root@<hostname>"
          
          # Change this to the ID-LINK of the desired disk shown by 'lsblk'
          clan.diskLayouts.singleDiskExt4 = {
            device = "/dev/disk/by-id/__CHANGE_ME__";
          }

          # ...
        };
      };     
    }
    ```

### Step 2. Detect hardware specific drivers

1. Generate a `hardware-configuration.nix` for your target computer

    ```bash
    ssh root@<target-computer> nixos-generate-config --no-filesystems --show-hardware-config > hardware-configuration.nix
    ```

2. Move the generated file into `machines/jon/hardware-configuration.nix` folder.

### Initialize the facts

!!! Info
    **All facts are automatically initialized.**

If you need additional help see our [facts chapter](./secrets.md)
