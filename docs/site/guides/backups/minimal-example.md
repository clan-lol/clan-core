# Minimal Example

Configure a peer-to-peer backup system through the inventory so your machines back up their state to other machines in the Clan.

## What is BorgBackup?

BorgBackup is a deduplicating backup program with support for encryption and compression.
It runs on Linux, macOS, and BSD, and can mount backup archives via FUSE.

While this guide uses BorgBackup, Clan supports other backup services too.

### Example Setup

In this example, we configure a backup system with three machines: `bob`, `jon`, and `alice`. The `bob` and `jon` machines will periodically back up their state folders to `alice`. The backups are encrypted for security.

```nix
inventory.instances = {
  borgbackup = {
    module = {
      name = "borgbackup";
      input = "clan-core";
    };
    roles.client.machines = {
        "bob" = {
            startAt = "*-*-* 04:00:00";
        };
        "jon" = { };
    };
    roles.server.machines = {
        "alice" = {
            address = "alice.example.org";
        };
    };
  };
};
```

## Roles

In a Clan Service, roles define how machines participate in the backup system. Each role applies specific Nix configurations to the machine.

- Client machines create backups and send them to designated destinations. Clients can back up to multiple destinations for redundancy.

- Server machines act as repositories, receiving and storing backups from clients. Servers can be dedicated backup nodes within your Clan network.

## Backup destinations

This service supports backups to multiple destinations:

- Local disk storage
- Your own borgbackup server (using the `server` role)
- Third-party services such as Hetzner's Storage Box

If BorgBackup does not meet your needs, you can implement your own backup Clan service.
