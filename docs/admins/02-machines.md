# 02 Machines with Clan

Integrating a new machine into your Clan environment is a very easy yet flexible process, allowing for a straight forward management of multiple NixOS configurations.

We'll walk you through adding a new computer to your Clan using a special tool that works through a USB stick.

## Installing a New Machine

Clan CLI, in conjunction with [nixos-anywhere](https://github.com/nix-community/nixos-anywhere), provides a seamless method for installing NixOS on various machines.
This process involves preparing a suitable hardware and disk partitioning configuration and ensuring the target machine is accessible via SSH.

### Step 0. Prerequisites

- [x] Two Computers: You'll need the computer you're setting up and another one to control the setup process. Both should be able to connect over the network using SSH. This is usually already done if you're working with servers from providers like Hetzner.
- [x] A clan machine configuration you want to deploy. [Check out our templates](/templates/new-clan/flake.nix)
- [x] Identify and prepare the USB Flash Drive

#### Prepare the USB Flash Drive

1. Insert your USB flash drive into your computer.

2. Identify your flash drive with `lsblk`

    ```shellSession
    $ lsblk
    NAME                                          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
    sdb                                             8:0    1 117,2G  0 disk
    └─sdb1                                          8:1    1 117,2G  0 part  /run/media/qubasa/INTENSO
    nvme0n1                                       259:0    0   1,8T  0 disk
    ├─nvme0n1p1                                   259:1    0   512M  0 part  /boot
    └─nvme0n1p2                                   259:2    0   1,8T  0 part
      └─luks-f7600028-9d83-4967-84bc-dd2f498bc486 254:0    0   1,8T  0 crypt /nix/store                                                                 /
    ```

    In this case it's `sdb`

3. Ensure all partitions on the drive are unmounted. Replace `sdb1` in the command below with your device identifier (like `sdc1`, etc.):

```bash
sudo umount /dev/sdb1
```

## Creating a Bootable USB Drive on Linux

To create a bootable USB flash drive with the NixOS installer:

### Step 1. Build the Installer Image

```bash
nix build git+https://git.clan.lol/clan/clan-core.git#install-iso
```

### Step 2. Write the Image to the USB Drive

Use the `dd` utility to write the NixOS installer image to your USB drive:

```bash
sudo dd bs=4M conv=fsync oflag=direct status=progress if=./result/stick.raw of=/dev/sd<X>
```

In case your USB device is `sdb` use `of=/dev/sdb`

### Step 3. Boot and Connect

After writing the installer to the USB drive, use it to boot the target machine.

> i.e. Plug it into the target machine and select the USB drive as a temporary boot device.

For most hardware you can find the Key-combination below:

- **Dell**: F12 (Boot Menu), F2/Del (BIOS Setup)
- **HP**: F9 (Boot Menu), Esc (Startup Menu)
- **Lenovo**: F12 (ThinkPad Boot Menu), F2/Fn+F2/Novo Button (IdeaPad Boot Menu/BIOS Setup)
- **Acer**: F12 (Boot Menu), F2/Del (BIOS Setup)
- **Asus**: F8/Esc (Boot Menu), F2/Del (BIOS Setup)
- **Toshiba**: F12/F2 (Boot Menu), Esc then F12 (Alternate Method)
- **Sony**: F11/Assist Button (Boot Menu/Recovery Options)
- **Samsung**: F2/F12/Esc (Boot Menu), F2 (BIOS Setup)
- **MSI**: F11 (Boot Menu), Del (BIOS Setup)
- **Apple**: Option (Alt) Key (Boot Menu for Mac)
- If your hardware was not listed read the manufacturers instructions how to enter the boot Menu/BIOS Setup.

**During Boot**

Select `NixOS` to boot into the clan installer

**After Booting**

The installer will display an IP address and a root password, which you can use to connect via SSH.

Alternatively you can also use the displayed QR code.

> Note: If your target machine is **accessible via SSH and runs NixOS**; You can skip preparing and booting from the USB stick.
>
> Use the clan CLI command (`clan machines install <my-machine> <target_host>`) to install your configuration remotely via SSH.

#### Prepare the USB Flash Drive

1. Insert your USB flash drive into your computer.

2. Identify your flash drive with `lsblk`

    ```shellSession
    $ lsblk
    NAME                                          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
    sdb                                             8:0    1 117,2G  0 disk
    └─sdb1                                          8:1    1 117,2G  0 part  /run/media/qubasa/INTENSO
    nvme0n1                                       259:0    0   1,8T  0 disk
    ├─nvme0n1p1                                   259:1    0   512M  0 part  /boot
    └─nvme0n1p2                                   259:2    0   1,8T  0 part
      └─luks-f7600028-9d83-4967-84bc-dd2f498bc486 254:0    0   1,8T  0 crypt /nix/store                                                                 /
    ```

    In this case it's `sdb`

3. Ensure all partitions on the drive are unmounted. Replace `sdb1` in the command below with your device identifier (like `sdc1`, etc.):

```bash
sudo umount /dev/sdb1
```

> Note: Repeat this command for all mounted partitions of your USB drive listed under `MOUNTPOINTS`.

## Creating a Bootable USB Drive on Linux

To create a bootable USB flash drive with the NixOS installer:

### Step 1. Build the Installer Image

```bash
nix build git+https://git.clan.lol/clan/clan-core.git#install-iso
```

### Step 2. Write the Image to the USB Drive

Use the `dd` utility to write the NixOS installer image to your USB drive:

```bash
sudo dd bs=4M conv=fsync oflag=direct status=progress if=./result/stick.raw of=/dev/sd<X>
```

> [!Note]:
> depending on your device speed this may take a couple of minutes

In case your USB device is `sdb` use `of=/dev/sdb`

### Step 3. Boot and Connect

After writing the installer to the USB drive, use it to boot the target machine.

> i.e. Plug it into the target machine and select the USB drive as a temporary boot device.

For most hardware you can find the Key-combination below:

- **Dell**: F12 (Boot Menu), F2/Del (BIOS Setup)
- **HP**: F9 (Boot Menu), Esc (Startup Menu)
- **Lenovo**: F12 (ThinkPad Boot Menu), F2/Fn+F2/Novo Button (IdeaPad Boot Menu/BIOS Setup)
- **Acer**: F12 (Boot Menu), F2/Del (BIOS Setup)
- **Asus**: F8/Esc (Boot Menu), F2/Del (BIOS Setup)
- **Toshiba**: F12/F2 (Boot Menu), Esc then F12 (Alternate Method)
- **Sony**: F11/Assist Button (Boot Menu/Recovery Options)
- **Samsung**: F2/F12/Esc (Boot Menu), F2 (BIOS Setup)
- **MSI**: F11 (Boot Menu), Del (BIOS Setup)
- **Apple**: Option (Alt) Key (Boot Menu for Mac)
- If your hardware was not listed read the manufacturers instructions how to enter the boot Menu/BIOS Setup.

**During Boot**

Select `NixOS` to boot into the clan installer

**After Booting**

The installer will display an IP address and a root password, which you can use to connect via SSH.

Alternatively you can also use the displayed QR code.

To be reachable the machine needs to be connected via LAN (recommended)

If you're using Wifi. Follow the next steps

#### Connect to a Wifi

```bash
iwctl
```

This will enter `iwd`

```bash
[iwd]#
```

Inside IWD run the following command to connect to your Wifi:

```bash
# Identify your network device.
device list
# Replace 'wlan0' with your device name
# Find your Wifi SSID.
station wlan0 scan
station wlan0 get-networks

# Replace your_ssid with the Wifi SSID
# Connect to your network.
station wlan0 connect your_ssid

# Verify you are connected
station wlan0 show
```

If the connection was successful you should see something like this:

```bash
State                 connected                                                                                                                    
Connected network     FRITZ!Box (Your router device)                                                                                                         
IPv4 address          192.168.188.50 (Your new local ip)
```

Use `ctrl-c` or `ctrl-d` to exit `IWD`

The displayed QR code and connection information get updated automatically, once your are connected.

VUG8n9yq0gDHy0zX

### Step 4. Finishing the installation

> IMPORTANT: Now use your main computer

Confirm the machine is reachable via SSH from your other computer.

```bash
ssh root@192.168.188.50
```

> Note:
> Currently in networks where the Router blocks DNS you cannot use the hostname and must use the ip address directly.
> We recommend to deploy using home/private-networks (i.e. FRITZ!Box / Corporate LAN).
> public-networks (i.e. university / airport / cafe) might not always work as expected.

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
We need to set the hardware specific `disk-id`

```nix
# flake.nix / configuration.nix
clan.diskLayouts.singleDiskExt4 = {
  device = "/dev/disk/by-id/nvme-eui.e8238fa6bf530001001b448b4aec2929";
}
```

Also set the targetHost: (in our case: user `root` hostname `jon`)

```nix
clan.networking.targetHost = pkgs.lib.mkDefault "root@jon"
```

With the target machine running Linux and accessible via SSH, execute the following command to install NixOS on the target machine, replacing `<target_host>` with the machine's hostname or IP address:

Before running the command make sure to `cd` into your `clan`

```bash
my-clan (main)> tree
.
├── flake.lock
├── flake.nix
└── machines
    └── jon
        └── configuration.nix
```

And verify the machine is detected from `clan CLI`

```bash
clan machines list
#> jon
```

**Finally** deployment time!

Use the following command to build and deploy the image via SSH onto your machine.

> Note: This may take a while for building and for the file transfer.

```bash
clan machines install my-machine <target_host>
```

#### 🎉 🚀 Your machine is all set up

---

## What's next ?

- [**Tweak Your Machine Setup**](#update-your-machines): Learn how to update an existing machine?

Coming Soon:

- **Join Your Machines in a Private Network:**: Stay tuned for steps on linking all your machines into a secure mesh network with Clan.

---

A concrete command in our example will look like this

```bash
clan machines install jon root@192.168.188.50
```

> Note: the CLI will ask:
> `Install jon to root@192.168.188.50? [y/N]`
> Confirm with `y` after checking that for correctness

If you didn't generate any secrets yet. The deployment command will fail (Don't worry you can re-run it). See [secrets-management](./secrets-management.md) for how to generate your initial secrets.

#### 🎉 🚀 Your machine is all set up

---

## What's next ?

- [**Tweak Your Machine Setup**](#update-your-machines): Learn how to update an existing machine?

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