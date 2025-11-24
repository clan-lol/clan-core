
This guide explains how to protect your data using Clan's integrated backup system. You'll learn how to define what to back up, configure backup destinations, automate the process, and restore data when needed. Clan uses [BorgBackup](https://www.borgbackup.org/) under the hood for secure, deduplicated, and encrypted backups.


## Basic File and Directory Backups

At its simplest, a state defines which folders to back up. This configuration goes in your machine's NixOS configuration.

### Example: Backing Up Application Data

```nix
{
  clan.core.state.nextcloud = {
    folders = [
      "/var/lib/nextcloud"  # Main application data
      "/etc/nextcloud"      # Configuration files
    ];
  };
}
```

**Key points:**
- Specify absolute paths to directories you want to protect
- Multiple folders can be listed per state
- The backup system will automatically include all files and subdirectories



## Hooks

Hooks allow you to execute custom scripts during the backup lifecycle. Use them to prepare data, stop services, or perform cleanup.

### Available Hook Types

| Hook | When It Executes | Common Use Cases |
|------|------------------|------------------|
| `preBackupScript` | Before backup starts | Stop services, dump databases, sync files |
| `postBackupScript` | After backup completes | Restart services, cleanup temp files |
| `preRestoreScript` | Before restoration starts | Prepare system, stop conflicting services |
| `postRestoreScript` | After restoration completes | Restart services, verify integrity |


### Example: Pre and Post Backup Scripts

In the following example, we configure the `nextcloud` service to:

1. Stop the relevant services before syncing its data.
2. Start the services back up after syncing its data.

```nix
clan.core.state.nextcloud = {
  folders = [ "/var/lib/nextcloud" ];
  preBackupScript = ''
    export PATH=${
      lib.makeBinPath [
        config.systemd.package
      ]
    }

      systemctl stop phpfpm-nextcloud.service
      systemctl stop nextcloud-cron.timer
  '';

  postBackupScript = ''
    export PATH=${
      lib.makeBinPath [
        config.systemd.package
      ]
    }

    systemctl start phpfpm-nextcloud.service
    systemctl start nextcloud-cron.timer
  '';
};
```

??? tip "Example: Pre and Post Restore Scripts"
    ```nix
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

---

## Database Backups

The manual approach above works, but Clan provides built-in support for PostgreSQL databases with proper integration.

### PostgreSQL Backup Integration

Enable PostgreSQL backups and define databases to protect:

```nix
{
  # Enable the PostgreSQL backup module
  clan.core.postgresql.enable = true;

  # Configure each database
  clan.core.postgresql.databases.nextcloud = {
    # Database creation options (runs on first setup)
    create = {
      TEMPLATE = "template0";
      LC_COLLATE = "C";
      LC_CTYPE = "C";
      ENCODING = "UTF8";
      OWNER = "nextcloud";
    };

    # Services to stop during restore (for consistency)
    restore.stopOnRestore = [
      "phpfpm-nextcloud.service"
      "nextcloud-cron.timer"
    ];
  };
}
```

**What this does:**

- Automatically dumps the database before each backup
- Stores dumps securely in the backup repository
- Manages service dependencies during restore
- Recreates the database with correct settings on new deployments






