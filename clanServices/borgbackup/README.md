## Usage

```nix
inventory.instances = {
  borgbackup = {
    module = {
      name = "borgbackup";
      input = "clan";
    };
    roles.client.machines."jon".settings = {
      destinations."storagebox" = {
        repo = "username@$hostname:/./borgbackup";
        rsh = ''ssh -oPort=23 -i /run/secrets/vars/borgbackup/borgbackup.ssh'';
      };
    };
    roles.server.machines = { };
  };
};
```

The input should be named according to your flake input. Jon is configured as a
client machine with a destination pointing to a Hetzner Storage Box.

## Overview

This guide explains how to set up and manage
[BorgBackup](https://borgbackup.readthedocs.io/) for secure, efficient backups
in a clan network. BorgBackup provides:

- Space efficient storage of backups with deduplication
- Secure, authenticated encryption
- Compression: lz4, zstd, zlib, lzma or none
- Mountable backups with FUSE
- Easy installation on multiple platforms: Linux, macOS, BSD, …
- Free software (BSD license).
- Backed by a large and active open-source community.

## Roles

### 1. Client

Clients are machines that create and send backups to various destinations. Each
client can have multiple backup destinations configured.

### 2. Server

Servers act as backup repositories, receiving and storing backups from client
machines. They can be dedicated backup servers within your clan network.

## Backup destinations

This service allows you to perform backups to multiple `destinations`.
Destinations can be:

- **Local**: Local disk storage
- **Server**: Your own borgbackup server (using the `server` role)
- **Third-party services**: Such as Hetzner's Storage Box

## State management

Backups are based on [states](/reference/clan.core/state/). A state defines
which files should be backed up and how these files are obtained through
pre/post backup and restore scripts.

Here's an example for a user application `linkding`:

In this example:

- `/data/podman/linkding` is the application's data directory
- `/var/backup/linkding` is the staging directory where data is copied for
  backup

```nix
clan.core.state.linkding = {
  folders = [ "/var/backup/linkding" ];

  preBackupScript = ''
    export PATH=${
      lib.makeBinPath [
        config.systemd.package
        pkgs.coreutils
        pkgs.rsync
      ]
    }

    service_status=$(systemctl is-active podman-linkding)

    if [ "$service_status" = "active" ]; then
      systemctl stop podman-linkding
      rsync -avH --delete --numeric-ids "/data/podman/linkding/" /var/backup/linkding/
      systemctl start podman-linkding
    fi
  '';

  postRestoreScript = ''
    export PATH=${
      lib.makeBinPath [
        config.systemd.package
        pkgs.coreutils
        pkgs.rsync
      ]
    }

    service_status="$(systemctl is-active podman-linkding)"

    if [ "$service_status" = "active" ]; then
      systemctl stop podman-linkding

      # Backup locally current linkding data
      cp -rp "/data/podman/linkding" "/data/podman/linkding.bak"

      # Restore from borgbackup
      rsync -avH --delete --numeric-ids /var/backup/linkding/ "/data/podman/linkding/"

      systemctl start podman-linkding
    fi
  '';
};
```

## Managing backups

### Listing states

To see which files (`states`) will be backed up on a specific machine, use:

```bash
clan state list jon
```

This will show all configured states for the machine `jon`, for example:

```text
· service: linkding
  folders:
  - /var/backup/linkding
  preBackupCommand: pre-backup-linkding
  postRestoreCommand: post-restore-linkding

· service: zerotier
  folders:
  - /var/lib/zerotier-one
```

### Creating backups

To create a backup of a machine (e.g., `jon`), run:

```bash
clan backups create jon
```

This will backup all configured states (`zerotier` and `linkding` in this
example) from the machine `jon`.

### Listing available backups

To see all available backups, use:

```bash
clan backups list
```

This will display all backups with their timestamps:

```text
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-jon-2025-07-22T19:40:10
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-jon-2025-07-23T01:00:00
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T01:00:00
storagebox::username@username.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T06:02:35
```

### Restoring backups

#### Full restoration

To restore all services from a backup:

```bash
clan backups restore jon borgbackup storagebox::u444061@u444061.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T06:02:35
```

#### Partial restoration

To restore only a specific service (e.g., `linkding`):

```bash
clan backups restore --service linkding jon borgbackup storagebox::u444061@u444061.your-storagebox.de:/./borgbackup::jon-storagebox-2025-07-24T06:02:35
```
