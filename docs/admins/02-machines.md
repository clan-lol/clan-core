# 02 Machines with Clan

Integrating a new machine into your Clan environment is a very easy yet flexible process, allowing for a straight forward management of multiple NixOS configurations.

We'll walk you through adding a new computer to your Clan.

## Installing a New Machine

Clan CLI, in conjunction with [nixos-anywhere](https://github.com/nix-community/nixos-anywhere), provides a seamless method for installing NixOS on various machines.

This process involves preparing a suitable hardware and disk partitioning configuration and ensuring the target machine is accessible via SSH.

### Step 0. Prerequisites

Boot the target machine using our [Clan Installer](./03-Installer.md). Which is recommended for ensuring most efficient workflows.

Alternatively you can use any linux machine if it is reachable via SSH and supports `kexec`.

Confirm the machine is reachable via SSH from your setup computer.

```bash
ssh root@<your_target_machine_ip>
```

- [x] **Two Computers**: You need one computer that you're getting ready (we'll call this the Target Computer) and another one to set it up from (we'll call this the Setup Computer). Make sure both can talk to each other over the network using SSH.
- [x] **Machine configuration**: You want to deploy. [Check out our templates](./99-templates.md)
- [x] Initialized secrets: See [secrets](./06-secrets.md) for how to initialize your secrets.
- [x] (Optional) USB Flash Drive with the [Clan Installer](./03-Installer.md)

### Step 1. Identify Target Disk-ID

```bash
lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
# Should print something like:
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

Now change the following lines of your configuration you want to deploy.
We need to set the hardware specific `disk-id` (i.e. `nvme-eui.e8238fa6bf530001001b448b4aec2929`)

```nix
# flake.nix / configuration.nix
clan.diskLayouts.singleDiskExt4 = {
  device = "/dev/disk/by-id/<MY_DISK_ID>";
}
```

Also set the targetHost: (i.e. user `root` hostname `jon`)
The hostname is the **machine name** by default

```nix
clan.networking.targetHost = pkgs.lib.mkDefault "root@jon"
```

`cd` into your `my-clan` directory

```bash
my-clan (main)> tree
.
├── flake.lock
├── flake.nix
└── machines
    └── jon
        └── configuration.nix
```

And verify the machine configuration is detected from `clan CLI`

```bash
clan machines list
#> jon
```

### Step 3. Deploy the machine

**Finally deployment time!** Use the following command to build and deploy the image via SSH onto your machine.

Replace `<target_host>` with the **installer's ip address**:

```bash
clan machines install my-machine <target_host>
```

> Note: This may take a while for building and for the file transfer.

#### 🎉 🚀 Your machine is all set up

---

## What's next ?

- [**Update a Machine**](#update-your-machines): Learn how to update an existing machine?

Coming Soon:

- **Join Your Machines in a Private Network:**: Stay tuned for steps on linking all your machines into a secure mesh network with Clan.

---

## Update Your Machines

Clan CLI enables you to remotely update your machines over SSH. This requires setting up a target address for each target machine.

### Setting the Target Host

Replace `host_or_ip` with the actual hostname or IP address of your target machine:

```bash
clan config --machine my-machine clan.networking.targetHost root@host_or_ip
```

> Note: The use of `root@` in the target address implies SSH access as the `root` user.
> Ensure that the root login is secured and only used when necessary.

### Updating Machine Configurations

Execute the following command to update the specified machine:

```bash
clan machines update my-machine
```

You can also update all configured machines simultaneously by omitting the machine name:

```bash
clan machines update
```

### Setting a Build Host

If the machine does not have enough resources to run the NixOS evaluation or build itself,
it is also possible to specify a build host instead.
During an update, the cli will ssh into the build host and run `nixos-rebuild` from there.

```bash
clan config --machine my-machine clan.networking.buildHost root@host_or_ip
```

### Excluding a machine from `clan machine update`

To exclude machines from beeing updated when running `clan machines update` without any machines specified,
one can set the `clan.deployment.requireExplicitUpdate` option to true:

```bash
clan config --machine my-machine clan.deployment.requireExplicitUpdate true
```

This is useful for machines that are not always online or are not part of the regular update cycle.

---

# TODO:
* TODO: How to join others people zerotier
  * `services.zerotier.joinNetworks = [ "network-id" ]`
* Controller needs to approve over webinterface or cli