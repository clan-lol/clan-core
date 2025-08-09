## Features

- Creates incremental snapshots using rsnapshot
- Supports multiple backup targets
- Mount/unmount hooks for external storage
- Pre/post backup hooks for custom scripts
- Configurable snapshot retention
- Automatic state folder detection

## Usage

Enable the localbackup service and configure backup targets:

```nix
instances = {
  localbackup = {
    module.name = "@clan/localbackup";
    module.input = "self";
    roles.default.machines."machine".settings = {
      targets.external= {
        directory = "/mnt/backup";
        mountpoint = "/mnt/backup";
      };
    };
  };
};
```

## Commands

The service provides these commands:

- `localbackup-create`: Create a new backup
- `localbackup-list`: List available backups
- `localbackup-restore`: Restore from backup (requires NAME and FOLDERS environment variables)
