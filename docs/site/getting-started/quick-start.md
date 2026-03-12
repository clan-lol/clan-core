# Quick Start (Physical Machine)

This page is the fastest way to install Clan on a physical machine.

If you want explanations or troubleshooting, see the full
[Getting Started (Physical Machine)](./getting-started-physical.md) guide.

!!! Note "Prerequisites"
    Nix installed, `~/.ssh/id_ed25519` keypair exists, USB drive (≥1.5 GB)

## Create the Clan

```bash
nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- init
```

Enter a name (e.g. `MY-CLAN-1`) and domain (e.g. `myclan1.lol`). Back up the age key when prompted.

```bash
cd MY-CLAN-1
direnv allow
```

### Create a Machine Configuration

```bash
clan machines create test-machine
```

Edit `clan.nix` — add under `inventory.machines`:

```nix
test-machine = {
    deploy.targetHost = "root@<IP-ADDRESS>"; # fill in after step 6
    tags = [ ];
};
```

### Add Your SSH Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Paste the output into the `"admin-machine-1"` line in `clan.nix`, replacing `PASTE_YOUR_KEY_HERE`. Verify with `clan show`.

### (Optional) Enable WiFi on Target

Add under `inventory.instances` in `clan.nix`:

```nix
wifi = {
  roles.default.machines."test-machine" = {
    settings.networks.home = { };
  };
};
```

### Create Installer USB

Download the installer ISO:

```bash
# x86_64
wget https://github.com/nix-community/nixos-images/releases/download/nixos-25.11/nixos-installer-x86_64-linux.iso

# aarch64 (ARM)
# wget https://github.com/nix-community/nixos-images/releases/download/nixos-25.11/nixos-installer-aarch64-linux.iso
```

Identify your USB device and flash the ISO:

```bash
lsblk                        # identify your USB device (e.g. sdb)
sudo dd if=nixos-installer-x86_64-linux.iso of=/dev/<USB_DEVICE> bs=4M status=progress conv=fsync
```

### Boot Target from USB

Boot the target machine from the USB drive. Note the IP address shown on screen, then update `clan.nix` with it.

!!! Tip "No IP?"
    Press Ctrl+C, run `nmtui`, connect to WiFi, then Ctrl+D to return.

### Get Hardware Config

```bash
clan machines init-hardware-config test-machine --target-host root@<IP-ADDRESS>
```

### Configure Disk

```bash
clan templates apply disk single-disk test-machine --set mainDisk ""
# note the disk ID from the error output, then re-run:
clan templates apply disk single-disk test-machine --set mainDisk "/dev/<DISK_ID>"
```

### Install

```bash
clan machines install test-machine --target-host root@<IP-ADDRESS>
```

!!! Tip "Sandbox error?"
    Run `clan vars generate test-machine --no-sandbox` first, then retry.

Remove USB before reboot.

### Connect

```bash
clan ssh test-machine
# if host ID error: run the ssh-keygen line shown, then retry
```

---

### Quick Reference: Managing Packages

Add packages in `clan.nix` under `inventory.instances`:

```nix
packages = {
  roles.default.machines."test-machine".settings = {
    packages = [ "bat" "btop" "tldr" ];
  };
};
```

Deploy changes:

```bash
clan machines update test-machine
```

To remove a package, delete it from the list and run `update` again.
