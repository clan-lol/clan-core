
# Disk Encryption

This guide walks you through setting up a ZFS system with native encryption and remote decryption via SSH. After completing this guide, your machine's root filesystem will be encrypted, and you will be able to unlock it remotely over the network during boot.

!!! Info "Secure Boot"
    This guide is compatible with systems that have [secure boot disabled](../guides/secure-boot.md). If you encounter boot issues, check if secure boot needs to be disabled in your UEFI settings.

## Disk Layout Configuration

Replace the highlighted lines below with your own disk ID.
You can find out your disk ID by running:
```bash
ssh root@nixos-installer.local lsblk --output NAME,ID-LINK,FSTYPE,SIZE,MOUNTPOINT
```


=== "**Single Disk**"
    - Copy the configuration below into `machines/<mymachine>/disko.nix`.
    - Don't forget to `git add machines/<mymachine>/disko.nix` so that Nix sees the file.

    ```nix title="disko.nix" hl_lines="21 81 87"
      --8<-- "docs/code-examples/disko-single-disk.nix"
    ```

    1. Hardcodes this disk as a bootable disk
    2. Marks the generated secret as needed during the partitioning phase, so it will be uploaded during installation
    3. Stalls the boot process until the decryption secret file appears at the expected location
    4. Tells ZFS to read the decryption passphrase from a file
    5. Replace with the disk ID from the `lsblk` output above



=== "**Raid 1**"
    - Copy the configuration below into `machines/<mymachine>/disko.nix`.
    - Don't forget to `git add machines/<mymachine>/disko.nix` so that Nix sees the file.

    ```nix title="disko.nix" hl_lines="21 81 82 88 89"
      --8<-- "docs/code-examples/disko-raid.nix"
    ```

    1. Hardcodes this disk as a bootable disk
    2. Marks the generated secret as needed during the partitioning phase, so it will be uploaded during installation
    3. Stalls the boot process until the decryption secret file appears at the expected location
    4. Tells ZFS to read the decryption passphrase from a file
    5. Replace with the disk IDs from the `lsblk` output above


## Initrd SSH Configuration

Next, copy the configuration below into `machines/<mymachine>/initrd.nix` and include it in your `configuration.nix`.
Don't forget to `git add machines/<mymachine>/initrd.nix` so that Nix sees the file.

```nix title="initrd.nix" hl_lines="41 29"
--8<-- "docs/code-examples/initrd.nix"
```

1. Replace `<My_SSH_Public_Key>` with your SSH public key.
2. Replace with the network driver used by the target device. You can find the correct module by running `nix shell nixpkgs#pciutils -c lspci -k` on the target.
3. Marks the generated secret as needed during the activation phase, so it will be available in the initrd.

## Installation

### Copy SSH Public Key

Before starting the installation, ensure that your SSH public key is on the NixOS installer.

Copy your public SSH key to the installer if you have not done so already:

```bash
ssh-copy-id root@nixos-installer.local -i ~/.config/clan/nixos-anywhere/keys/id_ed25519
```

### Prepare Disks and Install

1. SSH into the installer:

    ```bash
    ssh root@nixos-installer.local
    ```

2. Wipe the existing partition table from the target disk:

    ```bash
    blkdiscard /dev/disk/by-id/<installdisk>
    ```

3. Run kexec and partition the disks:

    ```bash
    clan machines install <mymachine> --target-host root@nixos-installer.local --phases kexec,disko
    ```

4. Check the logs for errors before proceeding.

5. Install NixOS onto the partitioned disks:

    ```bash
    clan machines install <mymachine> --target-host root@nixos-installer.local --phases install
    ```

6. Reboot the machine and remove the USB installer.

## Remote Decryption

After rebooting, the machine will pause in the initrd and wait for the encryption key before continuing to boot. You can verify connectivity by SSHing into the initrd environment:

```bash
ssh root@<your-machines-ip> -p 7172
```

To automate the decryption step, create the following script:

- Save it as `machines/<mymachine>/decrypt.sh`.
- Make it executable with `chmod +x machines/<mymachine>/decrypt.sh`.
- Run it whenever the machine boots to deliver the encryption key.

```bash title="decrypt.sh" hl_lines="4 5"
#!/usr/bin/env bash
set -euxo pipefail

HOST="192.0.2.1" # (1)
MACHINE="<mymachine>" # (2)
while ! ping -W 1 -c 1 "$HOST"; do
  sleep 1
done
while ! timeout --foreground 10 ssh -p 7172 "root@$HOST" true; do
  sleep 1
done

# Ensure that /run/partitioning-secrets/zfs/key only ever exists with the full key
clan vars get "$MACHINE" zfs/key | ssh -p 7172 "root@${HOST}" "mkdir -p /run/partitioning-secrets/zfs && cat > /run/partitioning-secrets/zfs/key.tmp && mv /run/partitioning-secrets/zfs/key.tmp /run/partitioning-secrets/zfs/key"
```

1. Replace with your machine's IP address
2. Replace with your machine's name
