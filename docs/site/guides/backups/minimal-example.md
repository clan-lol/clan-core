In this guide we will explain how to install a simple peer-to-peer backup system through the inventory. Such that machines will backup it's state to other machines in the clan, ensuring redundancy and data safety.


### What is BorgBackup?

BorgBackup is a powerful and efficient backup solution designed for secure and space-efficient backups. It offers features such as:

- **Deduplication**: Saves storage space by avoiding duplicate data.
- **Encryption**: Ensures backups are secure and authenticated.
- **Compression**: Supports multiple compression algorithms like lz4, zstd, zlib, and more.
- **FUSE Mounting**: Allows backups to be mounted as a file system.
- **Cross-Platform**: Works on Linux, macOS, BSD, and more.
- **Open Source**: Licensed under BSD and supported by an active community.


While this guide uses BorgBackup, you can also use other backup services supported by Clan, depending on your requirements.


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

In a Clan Service, roles define how machines participate in the backup system. Each role applies specific Nix configurations to the machine, enabling flexibility and scalability in your backup setup.

- **Client**: These machines create backups and send them to designated destinations. Clients can be configured to back up to multiple destinations, ensuring redundancy and reliability.

- **Server**: These machines act as repositories, receiving and securely storing backups from client machines. Servers can be dedicated backup nodes within your clan network, providing centralized storage for all backups.


## Backup destinations

This service allows you to perform backups to multiple `destinations`.
Destinations can be:

- **Local**: Local disk storage
- **Server**: Your own borgbackup server (using the `server` role)
- **Third-party services**: Such as Hetzner's Storage Box


However, if BorgBackup does not meet your needs, you can implement your own backup clan service.
