# Managing NixOS Machines with Clan

Integrating a new machine into your cLan environment is a very easy yet flexible process, allowing for the centralized management of multiple NixOS configurations.

The Guide below showcases how to introduce a new machine into an existing cLan setup.

## Installing a New Machine

Clan CLI, in conjunction with [nixos-anywhere](https://github.com/nix-community/nixos-anywhere), provides a seamless method for installing NixOS on various machines.
This process involves preparing a suitable hardware and disk partitioning configuration and ensuring the target machine is accessible via SSH.

### Prerequisites

- [x] A running Linux system with SSH on the target machine is required. This is typically pre-configured for many server providers.
- [x] For installations on physical hardware, create a NixOS installer image and transfer it to a bootable USB drive as described below.

## Creating a Bootable USB Drive on Linux

To create a bootable USB flash drive with the NixOS installer:

### Build the Installer Image

```bash
nix build git+https://git.clan.lol/clan/clan-core.git#install-iso
```

### Prepare the USB Flash Drive

1. Insert your USB flash drive into your computer.

2. Identify your flash drive with `lsblk`.
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

3. Ensure all partitions on the drive are unmounted. Replace `sdX` in the command below with your device identifier (like `sdb`, etc.):

    ```bash
    sudo umount /dev/sdb1
    ```

### Write the Image to the USB Drive

Use the `dd` utility to write the NixOS installer image to your USB drive:

  ```bash
  sudo dd bs=4M conv=fsync oflag=direct status=progress if=./result/stick.raw of=/dev/sd<X>
  ```

  In case your USB device is `sdb` use `of=/dev/sdb`



### Boot and Connect

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

### Finishing the installation

With the target machine running Linux and accessible via SSH, execute the following command to install NixOS on the target machine, replacing `<target_host>` with the machine's hostname or IP address:

```bash
clan machines install my-machine <target_host>
```

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
* clan facts generate
* clan machine check / build (CI is missing)
* TODO: How to join others people zerotier
  * `services.zerotier.joinNetworks = [ "network-id" ]`
* Controller needs to approve over webinterface or cli