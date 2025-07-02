# Deploy a machine

Now that you have created a new machine, we will walk through how to install it.

## Prerequisites

!!! important "General Requirements"
    - [x] RAM > 2GB
    - [x] **Two Computers**: You need one computer that you're getting ready (we'll call this the Target Computer) and another one to set it up from (we'll call this the Setup Computer). Make sure both can talk to each other over the network using SSH.
    - [x] **Machine configuration**: See our basic [adding and configuring machine guide](./add-machines.md)
    - [x] **Initialized secrets**: See [secrets](secrets.md) for how to initialize your secrets.

=== "**Physical Hardware**"

    - [x] **USB Flash Drive**: See [Clan Installer](installer.md)

    !!! Steps

        1. Create a NixOS installer image and transfer it to a bootable USB drive as described in the [installer](./installer.md).

        2. Boot the target machine and connect it to a network that makes it reachable from your setup computer.

=== "**Cloud VMs**"

    - [x] Any cloud machine if it is reachable via SSH and supports `kexec`.

    !!! Warning "NixOS can cause strange issues when booting in certain cloud environments."
        If on Linode: Make sure that the system uses Direct Disk boot kernel (found in the configuration pannel)

### Step 1. Setting `targetHost`

=== "flake.nix (flake-parts)"

    ```{.nix hl_lines="22"}
    {
        inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
        inputs.nixpkgs.follows = "clan-core/nixpkgs";
        inputs.flake-parts.follows = "clan-core/flake-parts";
        inputs.flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";

        outputs =
            inputs@{ flake-parts, ... }:
            flake-parts.lib.mkFlake { inherit inputs; } {
            systems = [
                "x86_64-linux"
                "aarch64-linux"
                "x86_64-darwin"
                "aarch64-darwin"
            ];
            imports = [ inputs.clan-core.flakeModules.default ];

            clan = {
                inventory.machines = {
                    jon = {
                        # targetHost will get picked up by cli commands
                        deploy.targetHost = "root@jon";
                    };
                };
            };
        };
    }
    ```

=== "flake.nix (classic)"

    ```{.nix hl_lines="14"}
    {
        inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
        inputs.nixpkgs.follows = "clan-core/nixpkgs";

        outputs =
            { self, clan-core, ... }:
            let
                clan = clan-core.lib.clan {
                    inherit self;

                    inventory.machines = {
                        jon = {
                            # targetHost will get picked up by cli commands
                            deploy.targetHost = "root@jon";
                        };
                    };
                };
            in
            {
                inherit (clan.config)
                    nixosConfigurations
                    nixosModules
                    clanInternals
                    darwinConfigurations
                    darwinModules
                    ;
            };
    }
    ```

!!! warning
    The use of `root@` in the target address implies SSH access as the `root` user.
    Ensure that the root login is secured and only used when necessary.

### Step 2. Identify the Target Disk

On the setup computer, SSH into the target:

```bash title="setup computer"
ssh root@<IP> lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
```

Replace `<IP>` with the machine's IP or hostname if mDNS (i.e. Avahi) is available.

Which should show something like:

```{.shellSession hl_lines="6" .no-copy}
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

Look for the top-level disk device (e.g., nvme0n1 or sda) and copy its `ID-LINK`. Avoid using partition IDs like `nvme0n1p1`.

In this example we would copy `nvme-eui.e8238fa6bf530001001b448b4aec2929`

!!! tip
    For advanced partitioning, see [Disko templates](https://github.com/nix-community/disko-templates) or [Disko examples](https://github.com/nix-community/disko/tree/master/example).

### Step 3. Fill in hardware specific machine configuration

Edit the following fields inside the `./machines/<machine_name>/configuration.nix`

<!-- Note: Use "jon" instead of "<machine>" as "<" is not supported in title tag -->

```nix title="./machines/jon/configuration.nix" hl_lines="12 15 19"
{
    imports = [
    # contains your disk format and partitioning configuration.
    ../../modules/disko.nix
    # this file is shared among all machines
    ../../modules/shared.nix
    # enables GNOME desktop (optional)
    ../../modules/gnome.nix
    ];

    # Put your username here for login
    users.users.user.name = "__YOUR_USERNAME__";

    # Replace this __CHANGE_ME__ with the copied result of the lsblk command
    disko.devices.disk.main.device = "/dev/disk/by-id/__CHANGE_ME__";

    # IMPORTANT! Add your SSH key here
    # e.g. > cat ~/.ssh/id_ed25519.pub
    users.users.root.openssh.authorizedKeys.keys = [ "__YOUR_SSH_KEY__" ];

    # ...
}
```

!!! Info "Replace `__YOUR_USERNAME__` with the ip of your machine, if you use avahi you can also use your hostname"
!!! Info "Replace `__CHANGE_ME__` with the appropriate `ID-LINK` identifier, such as `nvme-eui.e8238fa6bf530001001b448b4aec2929`"
!!! Info "Replace `__YOUR_SSH_KEY__` with your personal key, like `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILoMI0NC5eT9pHlQExrvR5ASV3iW9+BXwhfchq0smXUJ jon@jon-desktop`"

### Step 4. Deploy the machine

**Finally deployment time!** Use the following command to build and deploy the image via SSH onto your machine.

=== "**Image Installer**"

    The installer will generate a password and local addresses on boot, then run ssh with these preconfigured.
    The installer shows it's deployment relevant information in two formats, a text form, as well as a QR code.

    Sample boot screen shows:

    - Root password
    - IP address
    - Optional Tor and mDNS details

    ```{ .bash .annotate .no-copy .nohighlight}
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │ ┌───────────────────────────┐                                                       │
    │ │███████████████████████████│ # This is the QR Code (1)                             │
    │ │██ ▄▄▄▄▄ █▀▄█▀█▀▄█ ▄▄▄▄▄ ██│                                                       │
    │ │██ █   █ █▀▄▄▄█ ▀█ █   █ ██│                                                       │
    │ │██ █▄▄▄█ █▀▄ ▀▄▄▄█ █▄▄▄█ ██│                                                       │
    │ │██▄▄▄▄▄▄▄█▄▀ ▀▄▀▄█▄▄▄▄▄▄▄██│                                                       │
    │ │███▀▀▀ █▄▄█ ▀▄   ▄▀▄█   ███│                                                       │
    │ │██▄██▄▄█▄▄▀▀██▄▀ ▄▄▄ ▄▀█▀██│                                                       │
    │ │██ ▄▄▄▄▄ █▄▄▄▄ █ █▄█ █▀ ███│                                                       │
    │ │██ █   █ █ █  █ ▄▄▄  ▄▀▀ ██│                                                       │
    │ │██ █▄▄▄█ █ ▄ ▄    ▄ ▀█ ▄███│                                                       │
    │ │██▄▄▄▄▄▄▄█▄▄▄▄▄▄█▄▄▄▄▄█▄███│                                                       │
    │ │███████████████████████████│                                                       │
    │ └───────────────────────────┘                                                       │
    │ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
    │ │Root password: cheesy-capital-unwell  # password (2)                             │ │
    │ │Local network addresses:                                                         │ │
    │ │enp1s0           UP    192.168.178.169/24 metric 1024 fe80::21e:6ff:fe45:3c92/64 │ │
    │ │enp2s0           DOWN                                                            │ │
    │ │wlan0            DOWN # connect to wlan (3)                                      │ │
    │ │Onion address: 6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion    │ │
    │ │Multicast DNS: nixos-installer.local                                             │ │
    │ └─────────────────────────────────────────────────────────────────────────────────┘ │
    │ Press 'Ctrl-C' for console access                                                   │
    │                                                                                     │
    └─────────────────────────────────────────────────────────────────────────────────────┘
    ```

    1.  This is not an actual QR code, because it is displayed rather poorly on text sites.
        This would be the actual content of this specific QR code prettified:
        ```json
        {
            "pass": "cheesy-capital-unwell",
            "tor": "6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion",
            "addrs": [
            "2001:9e8:347:ca00:21e:6ff:fe45:3c92"
            ]
        }
        ```

        To generate the actual QR code, that would be displayed use:
        ```shellSession
        echo '{"pass":"cheesy-capital-unwell","tor":"6evxy5yhzytwpnhc2vpscrbti3iktxdhpnf6yim6bbs25p4v6beemzyd.onion","addrs":["2001:9e8:347:ca00:21e:6ff:fe45:3c92"]}' | nix run nixpkgs#qrencode -- -s 2 -m 2 -t utf8
        ```
    2.  The root password for the installer medium.
        This password is autogenerated and meant to be easily typeable.
    3.  See how to connect the installer medium to wlan [here](./installer.md#optional-connect-to-wifi-manually).

    !!! tip
        Use [KDE Connect](https://apps.kde.org/de/kdeconnect/) for easyily sharing QR codes from phone to desktop

=== "**Cloud VM**"

    Just run the command **Option B: Cloud VM** below

#### Deployment Commands

##### Using password auth

```bash
clan machines install [MACHINE] --target-host <IP> --update-hardware-config nixos-facter
```

##### Using QR JSON

```bash
clan machines install [MACHINE] --json "[JSON]" --update-hardware-config nixos-facter
```

##### Using QR image file

```bash
clan machines install [MACHINE] --png [PATH] --update-hardware-config nixos-facter
```

#### Option B: Cloud VM

```bash
clan machines install [MACHINE] --target-host <IP> --update-hardware-config nixos-facter
```

!!! success
    Your machine is all set up. 🎉 🚀

## Post-Deployment: Updating Machines

### Updating

Update a single machine:

```bash
clan machines update jon
```

Update all machines:

```bash
clan machines update
```

### Build Host Configuration

If a machine is too resource-limited, use another host.

If the machine does not have enough resources to run the NixOS evaluation or build itself,
it is also possible to specify a build host.

During an update, the CLI will SSH into the build host and run `nixos-rebuild` from there.

```{.nix hl_lines="5" .no-copy}
clan {
    # ...
    machines = {
        "jon" = {
            clan.core.networking.buildHost = "root@<host_or_ip>";
        };
    };
};
```

### Excluding from Automatic Updates

To exclude machines from being updated when running `clan machines update` without any machines specified,
one can set the `clan.core.deployment.requireExplicitUpdate` option to true:

```{.nix hl_lines="5" .no-copy}
clan {
    # ...
    machines = {
        "jon" = {
            clan.core.deployment.requireExplicitUpdate = true;
        };
    };
};
```

This is useful for machines that are not always online or are not part of the regular update cycle.

