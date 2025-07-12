# Deploy a machine

Now that you have created a machines, added some services and setup secrets. This guide will walk through how to deploy it.

## Prerequisites

!!! important "General Requirements"
    - [x] RAM > 2GB
    - [x] **Two Computers**: You need one computer that you're getting ready (we'll call this the Target Computer) and another one to set it up from (we'll call this the Setup Computer). Make sure both can talk to each other over the network using SSH.
    - [x] **Machine configuration**: See our basic [adding and configuring machine guide](./add-machines.md)
    - [x] **Initialized secrets**: See [secrets](secrets.md) for how to initialize your secrets.

## Physical Hardware

!!! note "skip this if using a cloud VM"

Steps:

- Create a NixOS installer image and transfer it to a bootable USB drive as described in the [installer](./installer.md).
- Boot the target machine and connect it to a network that makes it reachable from your setup computer.
- Note down a reachable ip adress (*ipv4*, *ipv6* or *tor*)

---

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
3.  See [how to connect to wlan](./installer.md#optional-connect-to-wifi-manually).

!!! tip
    Use [KDE Connect](https://apps.kde.org/de/kdeconnect/) for easyily sharing QR codes from phone to desktop

## Cloud VMs

!!! note "skip this if using a physical machine"

Clan supports any cloud machine if it is reachable via SSH and supports `kexec`.

Steps:

- Go to the configuration panel and note down how to connect to the machine via ssh.

!!! tip "NixOS can cause strange issues when booting in certain cloud environments."
    If on Linode: Make sure that the system uses "Direct Disk boot kernel" (found in the configuration panel)

## Setting `targetHost`

In your nix files set the targetHost (reachable ip) that you retrieved in the previous step.

```{.nix title="clan.nix" hl_lines="9"}
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "my-clan";

  inventory.machines = {
    # Define machines here.
    # The machine name will be used as the hostname.
    jon = {
        deploy.targetHost = "root@192.168.192.4"; # (1)
    };
  };
  # ...
  # elided
}
```

1. Use the ip address of your targetMachine that you want to deploy. If using the [flash-installer](./installer.md) it should display its local ip-address when booted.

!!! warning
    The use of `root@` in the target address implies SSH access as the `root` user.
    Ensure that the root login is secured and only used when necessary.

See also [how to set TargetHost](../target-host.md) for other methods.

## Retrieve the hardware report

By default clan uses [nixos-facter](https://github.com/nix-community/nixos-facter) which captures detailed information about the machine or virtual environment.

To generate the hardware-report (`facter.json`) run:

```bash
clan machines update-hardware-config <machineName>
```

Example output:

```shell-session
$ clan machines update-hardware-config jon
[jon] $ nixos-facter
Successfully generated: ./machines/jon/facter.json
```

See [update-hardware-config cli reference](../../reference/cli/machines.md#machines-update-hardware-config) for further configuration possibilities if needed.

## Configure your disk schema

By default clan uses [disko](https://github.com/nix-community/disko) which allows for declarative disk partitioning.

To setup a disk schema for a machine run

```bash
clan templates apply disk --to-machine jon --template single-disk --set mainDisk ""
```

Which should fail and give the valid options for the specific hardware:

```shellSession
Invalid value  for placeholder mainDisk - Valid options:
/dev/disk/by-id/nvme-WD_PC_SN740_SDDQNQD-512G-1201_232557804368
```

Re-run the command with the correct disk:

```bash
clan templates apply disk --to-machine jon --template single-disk --set mainDisk "/dev/disk/by-id/nvme-WD_PC_SN740_SDDQNQD-512G-1201_232557804368"
```

Should now be succesfull

```shellSession
Applied disk template 'single-disk' to machine 'jon'
```

A disko.nix file should be created in `machines/jon`
You can have a look and customize it if needed.

!!! tip
    For advanced partitioning, see [Disko templates](https://github.com/nix-community/disko-templates) or [Disko examples](https://github.com/nix-community/disko/tree/master/example).

## Deploy the machine

**Finally deployment time!** Use one of the following commands to build and deploy the image via SSH onto your machine.

### Deployment Commands

#### Using password auth

```bash
clan machines install [MACHINE] --target-host <IP> --update-hardware-config nixos-facter
```

#### Using QR JSON

```bash
clan machines install [MACHINE] --json "[JSON]" --update-hardware-config nixos-facter
```

#### Using QR image file

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
one can set the `clan.deployment.requireExplicitUpdate` option to true:

```{.nix hl_lines="5" .no-copy}
clan {
    # ...
    machines = {
        "jon" = {
            clan.deployment.requireExplicitUpdate = true;
        };
    };
};
```

This is useful for machines that are not always online or are not part of the regular update cycle.

