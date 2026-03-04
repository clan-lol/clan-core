---
description = "Single disk schema with a classic GPT layout, ext4 root filesystem"
---

This schema defines a traditional and highly compatible disk layout, supporting both modern EFI systems and legacy BIOS compatibility. It uses the reliable **ext4** filesystem for the root partition.

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

3. **Root Partition**
   - Size: Remaining disk space (`100%`).
   - Filesystem: `ext4`.
   - Mount Point: `/`.
