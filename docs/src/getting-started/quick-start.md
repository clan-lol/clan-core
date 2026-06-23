# Quick Start (Physical Machine)

This page is the fastest way to install Clan on a physical machine.

For detailed explanations or troubleshooting, see the full
[Getting Started (Physical Machine)](/docs/getting-started/getting-started-physical) guide.

:::admonition[Prerequisites]{type=note}
[Nix installed](/docs/getting-started/install-nix), `~/.ssh/id_ed25519` keypair exists, USB drive (≥1.5 GB)
:::

## Create the Clan

```bash
nix run https://clan.lol/install/{{ version }} --refresh -- init
```

This downloads the Clan CLI and walks you through creating a new clan project. Enter a name (e.g. `MY-CLAN-1`) and domain (e.g. `myclan1.lol`). Back up the age key when prompted.

```bash
cd MY-CLAN-1
direnv allow
```

This enters your new project directory and activates the development environment so all Clan tools are available.

## Create a Machine Configuration

Open `clan.nix`, and find the `inventory.machines` line:

```nix [clan.nix] {2,3,4,5}
inventory.machines = { # FIND THIS LINE, ADD THE FOLLOWING
    test-machine = {
        tags = [ "test" ];
    };
```

:::admonition[Note]{type=note}
The machine name `test-machine` is used throughout this guide and will be referenced by other machines and services. Changing it later requires updating all references.
:::

## Add Your SSH Key

```bash
cat ~/.ssh/id_ed25519.pub
```

This prints your public key. Copy the output and paste it into the `"admin-machine-1"` line in `clan.nix`, replacing `PASTE_YOUR_KEY_HERE`.

## (Optional) Enable WiFi on Target

Add under `inventory.instances` in `clan.nix`:

```nix
wifi = {
  roles.default.machines."test-machine" = {
    settings.networks.home = { };
  };
};
```

The WiFi configuration adds wireless support on the target machine after installation.

## Create Installer USB

For physical machines and Virtual Box, Download the installer ISO:

```bash
wget https://github.com/nix-community/nixos-images/releases/download/nixos-26.05/nixos-installer-x86_64-linux.iso
```

This downloads the NixOS installer image. For ARM machines, replace `x86_64` with `aarch64`.

**For Virtual Box**, use the above ISO to create a new virtual machine.

**For physical machines**, flash it to your USB drive:

```bash
lsblk
```

This lists all block devices. Find your USB drive by matching its size (e.g. `sdb`).

:::admonition[This will erase ALL data on the selected device]{type=danger}

Double-check that the device path (e.g. `/dev/sdb`) matches your USB drive before running the `dd` command.
:::

```bash
sudo dd if=nixos-installer-x86_64-linux.iso of=/dev/<USB_DEVICE> bs=4M status=progress conv=fsync
```

This writes the installer image to the USB drive. All existing data on the drive will be lost.

Boot the target machine from the USB drive. Note the **installer IP address** shown on screen — the following steps pass it to `--target-host`. After installation the machine reboots and gets a different IP, which you'll configure later.

:::admonition[No IP?]{type=tip}
Press Ctrl+C, run `nmtui`, connect to WiFi, then Ctrl+D to return.
:::

## Configure SSH access

```sh
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@<INSTALLER-IP>
```

```text
Number of key(s) added: 1
```

Confirm that you can login

```sh
ssh root@<INSTALLER-IP>
```

Should print

```sh
[root@nixos-installer:~]#
```

This authorizes your key for the running installer session so the following `clan`
commands can connect over SSH. It is not written to the USB drive, so repeat this
step if you reboot the installer.

## Get Hardware Config

```bash
clan machines init-hardware-config test-machine --target-host root@<INSTALLER-IP>
```

This detects the target machine's hardware (CPU, disks, network cards) and saves it to your project.

## Configure Disk

First, list available disks:

```bash
clan templates info disk test-machine ext4-single-disk
```

This will list available disk IDs. Find the correct one (typically starting with `/dev/disk/by-id/`), then run:

```bash
clan templates apply disk ext4-single-disk test-machine --set mainDisk "/dev/disk/by-id/..."
```

This assigns the disk that NixOS will be installed onto.

## Install

```bash
clan machines install test-machine --target-host root@<INSTALLER-IP>
```

This builds NixOS from your configuration and installs it on the target machine. You'll be prompted for confirmation, WiFi credentials, and a root password.

:::admonition[Sandbox error?]{type=tip}
Run `clan vars generate test-machine --no-sandbox` first, then retry.
:::

Remove the USB drive before the machine reboots.

## Configure How to Reach the Machine

After installation the machine reboots into the installed system, which gets a **new IP address**.

The installer IP is no longer valid. Find the new IP (check your router's DHCP leases, or log in locally and run `ip addr`), then tell Clan how to reach it by adding the `internet` instance.

Find the `inventory.instances` line in `clan.nix` and add:

```nix [clan.nix] {2-8}
  inventory.instances = { # FIND THIS LINE, ADD THE FOLLOWING
    internet = {
      roles.default.machines."test-machine" = {
        settings.host = "<MACHINE-IP>"; # REPLACE WITH THE INSTALLED MACHINE'S IP ADDRESS
        settings.user = "root";
      };
    };

```

`clan ssh` and `clan machines update` read this address to connect to the installed system.

## Connect

```bash
clan ssh test-machine
```

This opens an SSH session to your machine using the connection details from `clan.nix`. If you get a host identification error, run the `ssh-keygen` command shown in the output, then retry.

---

## Quick Reference: Managing Packages

Add packages in `clan.nix` under `inventory.instances`:

```nix
packages = {
  roles.default.machines."test-machine".settings = {
    packages = [ "bat" "btop" "tldr" ];
  };
};
```

This declares which extra packages should be present on the machine.

```bash
clan machines update test-machine
```

This builds and deploys the updated configuration to the target machine. To remove a package, delete it from the list and run `update` again.
