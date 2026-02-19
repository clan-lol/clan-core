# Clan Quick Start: Physical Machine

> **Prerequisites:** Nix installed, `~/.ssh/id_ed25519` keypair exists, USB drive (≥1.5 GB)
>
> See the [full guide](./getting-started-physical.md) for troubleshooting and detailed explanations.

---

### 1. Create the Clan

```bash
nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- init
```

Enter a name (e.g. `MY-CLAN-1`) and domain (e.g. `myclan1.lol`). Back up the age key when prompted.

```bash
cd MY-CLAN-1
direnv allow
```

### 2. Create a Machine Configuration

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

### 3. Add Your SSH Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Paste the output into the `"admin-machine-1"` line in `clan.nix`, replacing `PASTE_YOUR_KEY_HERE`. Verify with `clan show`.

### 4. (Optional) Enable WiFi on Target

Add under `inventory.instances` in `clan.nix`:

```nix
wifi = {
  roles.default.machines."test-machine" = {
    settings.networks.home = { };
  };
};
```

### 5. Create Installer USB

```bash
lsblk                        # identify your USB device (e.g. sdb)
sudo umount /dev/sdb*         # unmount all partitions
```

```bash
clan flash write --flake https://git.clan.lol/clan/clan-core/archive/main.tar.gz \
  --ssh-pubkey $HOME/.ssh/id_ed25519.pub \
  --keymap us \
  --language en_US.UTF-8 \
  --disk main /dev/<USB_DEVICE> \
  flash-installer
```

### 6. Boot Target from USB

Boot the target machine from the USB drive. Note the IP address shown on screen, then update `clan.nix` with it.

> **No IP?** Press Ctrl+C, run `nmtui`, connect to WiFi, then Ctrl+D to return.

### 7. Get Hardware Config

```bash
clan machines init-hardware-config test-machine --target-host root@<IP-ADDRESS>
```

### 8. Configure Disk

```bash
clan templates apply disk single-disk test-machine --set mainDisk ""
# note the disk ID from the error output, then re-run:
clan templates apply disk single-disk test-machine --set mainDisk "/dev/<DISK_ID>"
```

### 9. Install

```bash
clan machines install test-machine --target-host root@<IP-ADDRESS>
```

> **Sandbox error?** Run `clan vars generate test-machine --no-sandbox` first, then retry.

Remove USB before reboot.

### 10. Connect

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