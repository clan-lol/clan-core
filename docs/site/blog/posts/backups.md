---
title: "Dev Report: Declarative Backups and Restore"
description: "An extension to the NixOS module system to declaratively describe how application state is backed up and restored."
authors:
  - Mic92
date: 2024-06-24
slug: backups
---

Our goal with [Clan](https://clan.lol/) is to give users control over their data.
However, with great power comes great responsibility, and owning your data means you also need to take care of backups yourself.

In our experience, setting up automatic backups is often a tedious process as it requires custom integration of the backup software and
the services that produce the state. More importantly than the backup is the restore.
Restores are often not well tested or documented, and if not working correctly, they can render the backup useless.

In Clan, we want to make backup and restore a first-class citizen.
Every service should describe what state it produces and how it can be backed up and restored.

In this article, we will discuss how our backup interface in Clan works.
The interface allows different backup software to be used interchangeably and
allows module authors to define custom backup and restore logic for their services.


## First Comes the State

Our services are built from Clan modules. Clan modules are essentially [NixOS modules](https://wiki.nixos.org/wiki/NixOS_modules), the basic configuration components of NixOS.
However, we have enhanced them with additional features provided by Clan and restricted certain option types to enable configuration through a [graphical interface](https://docs.clan.lol/blog/2024/05/25/jsonschema-converter/).

In a simple case, this can be just a bunch of directories, such as what we define for our [ZeroTier](https://www.zerotier.com/) VPN service.

```nix
{
  clan.core.state.zerotier.folders =  [ "/var/lib/zerotier-one" ];
}
```

For other systems, we need more complex backup and restore logic.
For each state, we can provide custom command hooks for backing up and restoring.

In our PostgreSQL module, for example, we define `preBackupCommand` and `postRestoreCommand` to use `pg_dump` and `pg_restore` to backup and restore individual databases:

```nix
preBackupCommand = ''
  # ...
  runuser -u postgres -- pg_dump ${compression} --dbname=${db.name} -Fc -c > "${current}.tmp"
  # ...
'';
postRestoreCommand = ''
  # ...
  runuser -u postgres -- dropdb "${db.name}"
  runuser -u postgres -- pg_restore -C -d postgres "${current}"
  # ...
'';
```

## Then the Backup

Our CLI unifies the different backup providers in one [interface](https://docs.clan.lol/reference/cli/backups/).

As of now, we support backups using [BorgBackup](https://www.borgbackup.org/) and
a backup module called "localbackup" based on [rsnapshot](https://rsnapshot.org/), optimized for backup on locally-attached storage media.

To use different backup software, a module needs to set the options provided by our backup interface.
The following Nix code is a toy example that uses the `tar` program to perform backup and restore to illustrate how the backup interface works:

```nix
  clan.core.backups.providers.tar = {
    list = ''
      echo /var/lib/system-back.tar
    '';
    create = let
      uniqueFolders = lib.unique (
        lib.flatten (lib.mapAttrsToList (_name: state: state.folders) config.clan.core.state)
      );
    in ''
      # FIXME: a proper implementation should also run `state.preBackupCommand` of each state
      if [ -f /var/lib/system-back.tar ]; then
        tar -uvpf /var/lib/system-back.tar ${builtins.toString uniqueFolders}
      else
        tar -cvpf /var/lib/system-back.tar ${builtins.toString uniqueFolders}
      fi
    '';
    restore = ''
      IFS=':' read -ra FOLDER <<< "''$FOLDERS"
      echo "${FOLDER[@]}" > /run/folders-to-restore.txt
      tar -xvpf /var/lib/system-back.tar -C / -T /run/folders-to-restore.txt
    '';
  };
```

For better real-world implementations, check out the implementations for [BorgBackup](https://git.clan.lol/clan/clan-core/src/branch/main/clanModules/borgbackup/default.nix)
and [localbackup](https://git.clan.lol/clan/clan-core/src/branch/main/clanModules/localbackup/default.nix).

## What It Looks Like to the End User

After following the guide for configuring a [backup](https://docs.clan.lol/getting-started/backups/),
users can use the CLI to create backups, list them, and restore them.

Backups can be created through the CLI like this:

```
clan backups create web01
```

BorgBackup will also create backups itself every day by default.

Completed backups can be listed like this:

```
clan backups list web01
...
web01::u366395@u366395.your-storagebox.de:/./borgbackup::web01-web01-2024-06-18T01:00:00
web03::u366395@u366395.your-storagebox.de:/./borgbackup::web01-web01-2024-06-19T01:00:00
```
One cool feature of our backup system is that it is aware of individual services/applications.
Let's say we want to restore the state of our [Matrix](https://matrix.org/) chat server; we can just specify it like this:

```
clan backups restore --service matrix-synapse web01 borgbackup web03::u366395@u366395.your-storagebox.de:/./borgbackup::web01-web01-2024-06-19T01:00:00
```

In this case, it will first stop the matrix-synapse systemd service, then delete the [PostgreSQL](https://www.postgresql.org/) database, restore the database from the backup, and then start the matrix-synapse service again.

## Future work

As of now we implemented our backup and restore for a handful of services and we expect to refine the interface as we test the interface for more applications.

Currently, our backup implementation backs up filesystem state from running services.
This can lead to inconsistencies if applications change the state while the backup is running.
In the future, we hope to make backups more atomic by backing up a filesystem snapshot instead of normal directories.
This, however, requires the use of modern filesystems that support these features.
