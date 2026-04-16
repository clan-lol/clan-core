---
description = "Single disk schema with Btrfs subvolumes, Btrfs-based ephemeral root (rollback), and automated btrbk snapshots"
---

This schema defines a GPT-based disk layout optimized for a "stateless" NixOS configuration (see [nix-community/impermanance](https://github.com/nix-community/impermanence)). Unlike a `tmpfs` root, this setup uses a Btrfs subvolume for the root directory (`/`) that is automatically wiped and recreated on every boot. This approach provides the benefits of a fresh system state while allowing for easy inspection of previous boot states via archived subvolumes.

### Disk Overview

- Name: `main-{{uuid}}`
- Device: `{{mainDisk}}`

### Partitions

1. **BIOS Boot Partition**
    - Provides compatibility for MBR booting on GPT disks.
    - Size: `1M`
    - Type: `EF02`

2. **EFI System Partition (ESP)**
    - Size: `500M`
    - Type: `EF00`
    - Filesystem: `vfat`
    - Mount Point: `/boot`
    - Options: `umask=0077` (restrictive permissions for security).

3. **Btrfs Partition (Storage)**
    - Size: Remaining disk space (`100%`).
    - Filesystem: `btrfs`.
    - Subvolumes:
        - `@root`: Mounted at `/`. This subvolume is ephemeral (see Rollback Logic).
        - `@nix`: Mounted at `/nix`. Optimized with `compress=zstd` and `noatime`.
        - `@home`: Mounted at `/home`. Optimized with `compress=zstd`.
        - `@persist`: Mounted at `/persist`. Optimized with `compress=zstd`. Marked as `neededForBoot = true` to store persistent system state (machine-id, SSH keys, etc.).

### Ephemeral Root Logic (Btrfs Rollback)

This configuration implements statelessness via a systemd-initrd service that runs before the root filesystem is mounted. On every boot, the script mounts the top-level Btrfs partition and moves the existing `@root` subvolume into a directory named `root.old.d/`, timestamping it. The script automatically performs a recursive deletion of archived root subvolumes older than 30 days to manage disk space. A brand new, empty `@root` subvolume is created for the current session.

### Snapshot Management (btrbk)

The configuration includes automated local snapshots via [`btrbk`](https://digint.ch/btrbk/doc/readme.html) to ensure recovery options.

- Frequency: Every 2 hours (`0/2:00`).
- Retention:
    - `/nix`: 16 hourly, 7 daily, and 2 weekly snapshots.
    - `/home`: 16 hourly, 7 daily, 3 weekly, and 2 monthly snapshots.
- Minimum Guarantee: At least 3 days of snapshots are always preserved.

### Technical Implementation Notes

- Root Partition Reference: The rollback script targets the local variable `rootPartition` which is set to `${config.disko.devices.disk."main".device}-part3` by default. Ensure the partition matches the priority index in the `disko` config.
- Initrd: This setup requires `boot.initrd.systemd.enable = true` to handle the complex pre-mount logic.
