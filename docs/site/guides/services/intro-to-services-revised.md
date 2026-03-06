# Introduction to Clan Services

## 🚧 Early Draft Attempt — Under Active Development (but ready for brief review to make sure I'm on the right track)

A **service** is a reusable piece of functionality you can add to your machines. Services handle things like backups, networking, user management, and installing packages, all configured from your `clan.nix` file.

Instead of manually installing software and editing config files on each machine, you declare what services you want, and Clan sets everything up for you.


## The Basic Pattern

Every service follows the same pattern:

1. Add the service to `clan.nix`
2. Run `clan machines update <machine-name>`
3. The service is now running

## Your First Service: Installing Packages

The simplest service is `packages`, which installs software on your machines:

```nix
# clan.nix
inventory.instances = {
  packages = {
    roles.default.machines."test-machine".settings = {
      packages = [ "bat" "htop" "ripgrep" ];
    };
  };
};
```

Then deploy:

```bash
clan machines update test-machine
```

SSH into your machine:

```
clan ssh test-machine
```

and verify:

```bash
bat --version
htop --version
```

To remove a package, delete it from the list and run `update` again. That's declarative configuration, where your machine matches what's in your config file.

## Understanding Roles

Services have **roles** that define different behaviors. For example, a backup service has:

- **client** - machines that get backed up
- **server** - the machine that stores backups

```nix
inventory.instances = {
  borgbackup = {
    roles.client.machines."my-laptop" = {};
    roles.client.machines."my-desktop" = {};
    roles.server.machines."backup-server" = {};
  };
};
```

This says: "Back up my laptop and desktop to my backup server."

Different services have different roles. The `packages` service only has a `default` role. The `wireguard` VPN service has `controller` and `peer` roles. Check each service's documentation for its available roles.

## Using Tags

A tag is a label you attach to machines so you can reference them as a group. Think of it like labeling boxes when you move; you might label some "kitchen," some "bedroom," and some "office." Then when you want to do something to all kitchen boxes, you just look for that label.

Using tags, you can apply services to multiple machines at once. Every machine automatically has the `all` tag.

```nix
inventory.instances = {
  packages = {
    # Install these packages on ALL machines
    roles.default.tags.all.settings = {
      packages = [ "vim" "git" "curl" ];
    };
  };
};
```

You can also define custom tags in your machine definitions:

```nix
inventory.machines = {
  laptop = {
    deploy.targetHost = "root@192.168.0.10";
    tags = [ "workstation" ];
  };
  desktop = {
    deploy.targetHost = "root@192.168.0.11";
    tags = [ "workstation" ];
  };
  server = {
    deploy.targetHost = "root@192.168.0.12";
    tags = [ "server" ];
  };
};
```
Then you can use the above tags:

```nix
inventory.instances = {
  packages = {
    # Only workstations get these packages
    roles.default.tags.workstation.settings = {
      packages = [ "firefox" "vlc" ];
    };
    # Only servers get these packages
    roles.default.tags.server.settings = {
      packages = [ "nginx" "postgresql" ];
    };
  };
};
```

## Adding Settings

Most services have configurable settings. Here's the WiFi service with settings:

```nix
inventory.instances = {
  wifi = {
    roles.default.machines."my-laptop" = {
      settings.networks.home = {};
      settings.networks.office = {};
    };
  };
};
```

When you run `clan vars generate`, it will prompt you for the SSID and password for each network.

Here's borgbackup with settings:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.machines."my-laptop" = {
      settings.startAt = "*-*-* 02:00:00";  # Backup at 2 AM daily
    };
    roles.server.machines."backup-server" = {};
  };
};
```

## Combining Multiple Services

You can add as many services as you need:

```nix
inventory.instances = {
  # SSH access
  sshd = {
    roles.server.tags.all = {};
    roles.server.settings.authorizedKeys = {
      "admin" = "ssh-ed25519 AAAA... admin@example.com";
    };
  };

  # Install packages
  packages = {
    roles.default.tags.all.settings = {
      packages = [ "vim" "htop" ];
    };
  };

  # WiFi (for laptops)
  wifi = {
    roles.default.machines."laptop" = {
      settings.networks.home = {};
    };
  };

  # Backups
  borgbackup = {
    roles.client.tags.all = {};
    roles.server.machines."backup-server" = {};
  };
};
```

One `clan machines update` command applies all of these services.

## Available Services

Clan includes 30+ built-in services:

| Service | What It Does |
|---------|--------------|
| `packages` | Install packages from nixpkgs |
| `sshd` | SSH server with key management |
| `users` | User accounts and passwords |
| `wifi` | WiFi network configuration |
| `borgbackup` | Encrypted backups |
| `syncthing` | Peer-to-peer file sync |
| `wireguard` | VPN networking |
| `zerotier` | Mesh networking |
| `monitoring` | Prometheus + Grafana |
| `matrix-synapse` | Chat server |

See the full list in the [Services Reference](../services/definition.md).

## The Workflow

Here's the typical workflow when adding services:

```bash
# 1. Edit clan.nix to add/modify services

# 2. Generate any secrets (passwords, keys, etc.)
clan vars generate test-machine --no-sandbox  # --no-sandbox for Ubuntu

# 3. Deploy to the machine
clan machines update test-machine

# 4. Verify on the machine
ssh root@<ip>
```

## What's Happening Under the Hood

When you run `clan machines update`:

1. Clan builds a NixOS configuration that includes your services
2. The configuration is uploaded to the target machine
3. `nixos-rebuild switch` runs on the target
4. The machine is now running your services

No manual steps on the target machine. No logging in to install packages or edit config files. Everything is defined in your `clan.nix` and applied with one command.

## Next Steps

- [Introduction to Clan Vars](../vars/intro-to-vars-revised.md) - Learn how secrets and generated values work [NOTE: I'M CURRENTLY BUILDING THIS DOCUMENT TOO, BUT HAVEN'T PUSHED IT UP]
- [Services Reference](../../services/definition.md) - See all available services
