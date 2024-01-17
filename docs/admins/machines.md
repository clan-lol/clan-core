# Managing NixOS Machines

## Add Your First Machine

To start managing a new machine, use the following commands to create and then list your machines:

```shellSession
$ clan machines create my-machine
$ clan machines list
my-machine
```

## Configure Your Machine

In the example below, we demonstrate how to add a new user named `my-user` and set a password. This user will be configured to log in to the machine `my-machine`.

### Creating a New User

```shellSession
# Add a new user
$ clan config --machine my-machine users.users.my-user.isNormalUser true

# Set a password for the user
$ clan config --machine my-machine users.users.my-user.hashedPassword $(mkpasswd)
```

_Note: The `$(mkpasswd)` command generates a hashed password. Ensure you have the `mkpasswd` utility installed or use an alternative method to generate a secure hashed password._

## Test Your Machine Configuration Inside a VM

Before deploying your configuration to a live environment, you can run a virtual machine (VM) to test the settings:

```shellSession
$ clan vms run my-machine
```

This command run a VM based on the configuration of `my-machine`, allowing you to verify changes in a controlled environment.

## Installing a New Machine

Clan CLI, in conjunction with [nixos-anywhere](https://github.com/nix-community/nixos-anywhere), provides a seamless method for installing NixOS on various machines.
This process involves preparing a suitable hardware and disk partitioning configuration and ensuring the target machine is accessible via SSH.

### Prerequisites

- A running Linux system with SSH on the target machine is required. This is typically pre-configured for many server providers.
- For installations on physical hardware, create a NixOS installer image and transfer it to a bootable USB drive as described below.

## Creating a Bootable USB Drive on Linux

To create a bootable USB flash drive with the NixOS installer:

1. **Build the Installer Image**:

   ```shellSession
   $ nix build git+https://git.clan.lol/clan/clan-core.git#install-iso
   ```

2. **Prepare the USB Flash Drive**:

   - Insert your USB flash drive into your computer.
   - Identify your flash drive with `lsblk`. Look for the device with a matching size.
   - Ensure all partitions on the drive are unmounted. Replace `sdX` in the command below with your device identifier (like `sdb`, etc.):

     ```shellSession
     sudo umount /dev/sdX*
     ```

3. **Write the Image to the USB Drive**:

   - Use the `dd` utility to write the NixOS installer image to your USB drive:

     ```shellSession
     sudo dd bs=4M conv=fsync oflag=direct status=progress if=./result/stick.raw of=/dev/sdX
     ```

4. **Boot and Connect**:
   - After writing the installer to the USB drive, use it to boot the target machine.
   - The installer will display an IP address and a root password, which you can use to connect via SSH.

### Finishing the installation

With the target machine running Linux and accessible via SSH, execute the following command to install NixOS on the target machine, replacing `<target_host>` with the machine's hostname or IP address:

```shellSession
$ clan machines install my-machine <target_host>
```

## Update Your Machines

Clan CLI enables you to remotely update your machines over SSH. This requires setting up a deployment address for each target machine.

### Setting the Deployment Address

Replace `host_or_ip` with the actual hostname or IP address of your target machine:

```shellSession
$ clan config --machine my-machine clan.networking.deploymentAddress root@host_or_ip
```

_Note: The use of `root@` in the deployment address implies SSH access as the root user. Ensure that the root login is secured and only used when necessary._

### Updating Machine Configurations

Execute the following command to update the specified machine:

```shellSession
$ clan machines update my-machine
```

You can also update all configured machines simultaneously by omitting the machine name:

```shellSession
$ clan machines update
```
