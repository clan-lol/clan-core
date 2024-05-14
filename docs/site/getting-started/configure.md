# Configuration - How to configure clan with your own machines

## Global configuration

In the `flake.nix` file:

- [x] set a unique `clanName`.
- [ ] set `clanIcon` (optional)
- [ ] Set `machineIcon` per machine (optional)

These icons will be used by our future GUI.

=== "**buildClan**"

    ```nix title="clan-core.lib.buildClan"
    buildClan {
        # Set a unique name 
        clanName = "Lobsters";
        # Optional, a path to an image file
        clanIcon = ./path/to/file; 
        # Should usually point to the directory of flake.nix
        directory = ./.;

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

=== "**flakeParts**"

    !!! info "See [Clan with flake-parts](./flake-parts.md) for help migrating to flake-parts."

    ```nix title="clan-core.flakeModules.default"
    clan = {
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
    };
    ```

## Machine configuration

Adding or configuring a new machine requires two simple steps:

### Step 1. Identify Target Disk-ID

1. Find the remote disk id by executing:

    ```bash title="setup computer"
    ssh root@flash-installer.local lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
    ```

    !!! Note
        Replace `flash-installer.local` with the IP address of the machine if you don't have the avahi service running which resolves mDNS local domains.

    Which should show something like:

    ```bash hl_lines="6"
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

1. Edit the following fields inside the `flake.nix`

    === "**buildClan**"

        ```nix title="clan-core.lib.buildClan" hl_lines="18 23"
        buildClan {
          # ...
          machines = {
            "jon" = {
              imports = [
                # ...
                ./modules/disko.nix
                ./machines/jon/configuration.nix
              ];
              # ...

              # Change this to the correct ip-address or hostname
              # The hostname is the machine name by default
              clan.networking.targetHost = pkgs.lib.mkDefault "root@jon"

              # Change this to the ID-LINK of the desired disk shown by 'lsblk'
              disko.devices.disk.main = {
                device = "/dev/disk/by-id/__CHANGE_ME__";
              }

              # e.g. > cat ~/.ssh/id_ed25519.pub
              users.users.root.openssh.authorizedKeys.keys = [
                  "<YOUR SSH_KEY>"
              ];
              # ...
            };
          };
        }
        ```

    === "**flakeParts**"

        ```nix title="clan-core.flakeModules.default" hl_lines="18 23"
        clan = {
          # ...
          machines = {
            "jon" = {
              imports = [
                # ...
                ./modules/disko.nix
                ./machines/jon/configuration.nix
              ];
              # ...

              # Change this to the correct ip-address or hostname
              # The hostname is the machine name by default
              clan.networking.targetHost = pkgs.lib.mkDefault "root@jon"

              # Change this to the ID-LINK of the desired disk shown by 'lsblk'
              disko.devices.disk.main = {
                device = "/dev/disk/by-id/__CHANGE_ME__";
              }

              # e.g. > cat ~/.ssh/id_ed25519.pub
              users.users.root.openssh.authorizedKeys.keys = [
                  "__YOUR_SSH_KEY__"
              ];
              # ...
            };
          };
        };
        ```


!!! Info "Replace `__CHANGE_ME__` with the appropriate identifier, such as `nvme-eui.e8238fa6bf530001001b448b4aec2929`"
!!! Info "Replace `__YOUR_SSH_KEY__` with your personal key, like `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILoMI0NC5eT9pHlQExrvR5ASV3iW9+BXwhfchq0smXUJ jon@jon-desktop`"

These steps will allow you to update your machine later.

#### Step 2: Detect Drivers
Generate the `hardware-configuration.nix` file for your machine using the following command:

```bash
ssh root@flash-installer.local nixos-generate-config --no-filesystems --show-hardware-config > machines/jon/hardware-configuration.nix
```

#### Step 3: Custom Disk Formatting
In `./modules/disko.nix` a simple `ext4` disk partioning is defined for the disko module.
If you want a more complicated disk partioning setup look into the [disko examples](https://github.com/nix-community/disko/tree/master/example)


#### Step 4: Custom Configuration
In `./machines/jon/configuration.nix`, you can personalize the settings to suit your needs.



---

## Whats next?

- [Secrets & Facts](secrets.md): Setting up secrets with nix-sops

---
