# Introduction to Clan Backups

This guide explains how to use the Clan backup and state management interface to configure, manage, and restore backups for your services and machines. By the end of this guide, you will understand how to define backup states, manage backups, and restore data.

## State Management

Clan backups are based on the concept of [states](../../reference/clan.core/state.md). A state is a Nix attribute set, defined as `clan.core.state.<name> = {};`, which specifies the files or directories to back up.

For example, if you have a clan service called `linkding`, you can define the folders to back up as follows:

```nix hl_lines="2"
clan.core.state.linkding = {
  folders = [ "/var/backup/linkding" ];
};
```

In this example:

- `/var/backup/linkding` is the staging directory where data is prepared for backup.

This simple configuration ensures that all critical data for the `linkding` service is included in the backup process.


## Custom Pre and Post Backup Hooks

The state interface allows you to run custom scripts before creating a backup, after creating a backup, and after restoring one. These scripts are defined using the `preBackupScript`, `postBackupScript`, and `postRestoreScript` options. This can be useful for tasks like stopping services, syncing data, or performing cleanup operations.

### Example: Pre and Post Backup Scripts for the `linkding` Service

In the following example, we configure the `linkding` service to:

1. Stop the service before syncing its data.
2. Sync the data to a staging directory.
3. Start the service after sync
4. Clean the staging directory
5. Restore the data and restart the service after restoration.

```nix hl_lines="5 26"
clan.core.state.linkding = {
  folders = [ "/var/backup/linkding" ];

  # Script to run before creating a backup
  preBackupScript = ''
    export PATH=${
      lib.makeBinPath [
        config.systemd.package
        pkgs.coreutils
        pkgs.rsync
      ]
    }

    # Check if the service is running
    service_status=$(systemctl is-active podman-linkding)

    if [ "$service_status" = "active" ]; then
      # Stop the service and sync data to the backup directory
      systemctl stop podman-linkding
      rsync -avH --delete --numeric-ids "/data/podman/linkding/" /var/backup/linkding/
      systemctl start podman-linkding
    fi
  '';

  postBackupScript = ''
    shopt -s dotglob
    rm -r /var/backup/linkding/*
  '';

  # Script to run after restoring a backup
  postRestoreScript = ''
    export PATH=${
      lib.makeBinPath [
        config.systemd.package
        pkgs.coreutils
        pkgs.rsync
      ]
    }

    # Check if the service is running
    service_status="$(systemctl is-active podman-linkding)"

    if [ "$service_status" = "active" ]; then
      # Stop the service
      systemctl stop podman-linkding

      # Backup current data locally
      cp -rp "/data/podman/linkding" "/data/podman/linkding.bak"

      # Restore data from the backup directory
      rsync -avH --delete --numeric-ids /var/backup/linkding/ "/data/podman/linkding/"

      # Restart the service
      systemctl start podman-linkding
    fi
  '';
};
```
