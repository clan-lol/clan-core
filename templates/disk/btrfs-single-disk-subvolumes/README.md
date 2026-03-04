---
description = "Single disk schema with Btrfs subvolumes and automated btrbk snapshots"
---

This schema defines a standard GPT-based disk layout utilizing [btrfs-subvolume](https://www.man7.org/linux//man-pages/man8/btrfs-subvolume.8.html) for organized and convenient data management.

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
   - Label: `root`.
   - Subvolumes:
     - `@root`: Mounted at `/`. The standard persistent root directory.
     - `@nix`: Mounted at `/nix`. Optimized with `compress=zstd` and `noatime` to improve performance and reduce SSD wear.
     - `@home`: Mounted at `/home`. Optimized with `compress=zstd` for user data.

### Snapshot Management (btrbk)

The configuration includes automated local snapshots via [`btrbk`](https://digint.ch/btrbk/doc/readme.html) to ensure recovery options.

- Frequency: Every 2 hours (`*/2:00`).
- Retention:
  - `/nix`: 16 hourly, 7 daily, and 2 weekly snapshots.
  - `/home`: 16 hourly, 7 daily, 3 weekly, and 2 monthly snapshots.
- Minimum Guarantee: At least 3 days of snapshots are always preserved.
