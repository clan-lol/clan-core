---
description = "Single disk schema with Btrfs subvolumes, ephemeral tmpfs root, and automated btrbk snapshots"
---

This schema defines a sophisticated GPT-based disk layout designed for a "stateless" NixOS configuration (see [nix-community/impermanance](https://github.com/nix-community/impermanence)). It uses a `tmpfs` for the root directory (wiping state on reboot) while persisting specific data via Btrfs subvolumes. It also includes automated snapshot management for data integrity.

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

3. **Swap Partition**
    - Default size: `8G`; *adjust* to your RAM needs
    - Discard Policy: `both` (enables SSD TRIM support for swap).

4. **Btrfs Partition (Storage)**
    - Size: Remaining disk space (`100%`).
    - Filesystem: `btrfs`.
    - Subvolumes:
      - `@nix`: Mounted at `/nix`. Optimized with `compress=zstd` and `noatime` to reduce wear and improve performance.
      - `@home`: Mounted at `/home`. Optimized with `compress=zstd`.
      - `@persist`: Mounted at `/persist`. Optimized with `compress=zstd`. This subvolume is marked as `neededForBoot = true` to ensure persistent configuration/secrets are available early in the boot process.

### Ephemeral Root (tmpfs)

All data written to the root directory (outside of the Btrfs subvolumes) is stored in RAM and lost upon reboot. This ensures a clean system state every time the machine starts.

- Mount Point: `/`
- Size: `3G`
- Mode: `0755`

### Snapshot Management (btrbk)

The configuration includes automated local snapshots via [`btrbk`](https://digint.ch/btrbk/doc/readme.html) to ensure recovery options.

- Frequency: Every 2 hours (`*/2:00`).
- Retention:
  - `/nix`: 16 hourly, 7 daily, and 2 weekly snapshots.
  - `/home`: 16 hourly, 7 daily, 3 weekly, and 2 monthly snapshots.
- Minimum Guarantee: At least 3 days of snapshots are always preserved.
