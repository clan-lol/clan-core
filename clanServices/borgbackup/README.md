## Usage

```nix
inventory.instances = {
  borgbackup = {
    module = {
      name = "borgbackup";
      input = "clan-core";
    };
    roles.client.machines."jon".settings = {
      destinations."storagebox" = {
        repo = "username@hostname:/./borgbackup";
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

For a more comprehensive guide on backups look into the guide section.
