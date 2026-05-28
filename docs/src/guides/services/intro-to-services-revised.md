# Introduction to Clan Services

Imagine you're managing machines for a small team: Sally and Fred each have a laptop, and there's a shared backup server. You want WiFi configured on the laptops, nightly backups to the server, a user account for each person on their own machine, and SSH access across the board.

Without Clan, you'd handle each machine by hand: SSH in, install packages, edit config files, restart services, and repeat for every machine. Add a new laptop and you start again. Forget one step and the machine is inconsistent with the rest.

**Services** are how Clan handles this. A service is a pre-built, configurable module that handles one specific job. You declare which services run on which machines in `clan.nix`, Clan builds the configuration, and deploying is a single command.

## What Is a Service?

Clan comes with a library of services covering common infrastructure tasks: SSH, WiFi, user accounts, backups, networking, package installation, and more. Each service knows how to configure a machine for its specific job. You don't write the configuration yourself; you declare that you want the service, supply any settings it needs, and Clan takes care of the rest.

Services live in the `instances` section of your `clan.nix` file:

```nix
inventory.instances = {
  sshd = {
    roles.server.tags = [ "all" ];
  };
};
```

This says: run the `sshd` service, and give every machine the `server` role. Clan figures out what configuration that requires and applies it when you deploy.

## Your First Service

The simplest service is `packages`, which installs software on your machines. Here's how to add it:

```nix
inventory.instances = {
  packages = {
    roles.default.machines."sally-laptop" = {
      settings.packages = [ "bat" "htop" "ripgrep" ];
    };
  };
};
```

Once you've saved `clan.nix`, deploy the change. If this is the first time for this machine, use `install`:

```bash
clan machines install sally-laptop
```

Or if this isn't the first time, use update:

```bash
clan machines update sally-laptop
```

That's the deploy steps: create a `clan.nix`, run `install` or `update`, and you're all set. Clan builds a NixOS configuration that includes your services, uploads it to the machine, and runs `nixos-rebuild switch`. No manual steps on the target.

Some services need secrets before they can run: passwords, encryption keys, network credentials. For those, generate the secrets first, then deploy:

```bash
clan vars generate sally-laptop
clan machines install sally-laptop
```

`clan vars generate` prompts you for any secrets the service needs and stores them securely. You only need to run it when you add a new service or when secrets change. Simple services like `packages` don't need it.

To verify the packages landed, SSH in and check:

```bash
clan ssh sally-laptop
bat --version
```

To remove a package, delete it from the list and run `clan machines update`. The machine will match whatever is in the config file. That's declarative configuration.

## Roles

When a service runs across multiple machines, each machine may play a different part. A **role** defines what that part is.

The `borgbackup` service is a good example. It needs two kinds of machines: ones that get backed up, and one that stores the backups. It uses roles to tell them apart:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.machines."sally-laptop" = {};
    roles.client.machines."fred-laptop" = {};
    roles.server.machines."backup-server" = {};
  };
};
```

The `client` role configures a machine to send backups. The `server` role configures a machine to receive and store them. Clan applies the right configuration to each machine based on the role you've assigned.

Simple services, where every machine does the same job, use a single role called `default`. The `packages` service works this way: every machine in the `default` role gets the same treatment. More involved services define multiple named roles.

Each service's documentation describes what roles are available and what each one does.

## Tags

Naming machines one by one works fine for small setups, but it gets unwieldy as your fleet grows. **Tags** let you refer to groups of machines by label instead.

You apply tags in the `machines` section of `clan.nix`:

```nix
inventory.machines = {
  sally-laptop = {
    tags = [ "laptop" ];
  };
  fred-laptop = {
    tags = [ "laptop" ];
  };
  backup-server = {
    tags = [ "server" ];
  };
};
```

Then, instead of listing machines by name in your service, you reference the tag:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.server.machines."backup-server" = {};
  };
};
```

Clan resolves the tag to all machines that carry it. When Barb joins the team with a new laptop, you tag it `laptop` and she automatically gets backed up. You don't touch the service declaration at all.

Clan defines at least three tags automatically:

| Tag | Matches |
|-----|---------|
| `all` | Every machine in your inventory |
| `nixos` | Every machine with `machineClass = "nixos"` |
| `darwin` | Every machine with `machineClass = "darwin"` |

You define the rest by putting them in the `tags` list on each machine.

You can also mix tags and machine names within the same role. If most of your backup clients are laptops but you also want to include one specific desktop:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.client.machines."office-desktop" = {};
    roles.server.machines."backup-server" = {};
  };
};
```

Clan combines both into one group.

## Settings

Services are configurable through the `settings` attribute. Settings can apply to all machines in a role, or be overridden per machine.

**Role-wide settings** apply to every machine in a role:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.client.settings.startAt = "*-*-* 02:00:00";
    roles.server.machines."backup-server" = {};
  };
};
```

**Per-machine settings** apply only to one machine, layered on top of the role-wide settings:

```nix
inventory.instances = {
  wifi = {
    roles.default.tags = [ "laptop" ];
    roles.default.settings.networks.home = {};
    roles.default.machines."sally-laptop" = {
      settings.networks.office = {};
    };
    roles.default.machines."fred-laptop" = {};
  };
};
```

Per-machine settings merge on top of role-wide settings, so you only need to specify what's different. The role provides the `home` network to every laptop. Sally's entry adds `office` on top of that; she ends up with both. Fred's entry is empty, so he gets only what the role provides.

A note on `= {}`: throughout these examples you will see attributes assigned to an empty set. In Nix, this is how you say "include this, but I have nothing extra to specify." When you write `roles.default.machines."fred-laptop" = {}`, you are adding Fred's laptop to the role with no per-machine customization. When you write `settings.networks.home = {}`, you are enabling that network with its default settings. The key being present is the declaration; the empty braces mean there is nothing to add.

## Multiple Instances

Sometimes you need the same service configured differently for different machines. The `users` service is a good example: each person needs their own account, with their own username, on their own machine.

By default, the instance name in `clan.nix` is also the service module name. You can run the same service multiple times by giving each instance its own name and setting `module.name` to the name of the service:

```nix
inventory.instances = {
  user-sally = {
    module.name = "users";
    roles.default.machines."sally-laptop" = {};
    roles.default.settings.user = "sally";
  };
  user-fred = {
    module.name = "users";
    roles.default.machines."fred-laptop" = {};
    roles.default.settings.user = "fred";
  };
};
```

The `module.name` field tells Clan which service module to use. The instance names (`user-sally`, `user-fred`) can be anything; they just can't share a name.

> **Note:** Not every service supports multiple instances. Check the service documentation before setting up more than one.

---

## Available Services

Clan includes 50+ built-in services. Here is a small sampling:

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

See the full list in the [Services Reference](/docs/services/definition).

## Putting It All Together

Here is the scenario from the opener, fully wired up:

```nix
inventory.machines = {
  sally-laptop = {
    tags = [ "laptop" ];
  };
  fred-laptop = {
    tags = [ "laptop" ];
  };
  backup-server = {
    tags = [ "server" ];
  };
};

inventory.instances = {
  # Networking: direct SSH to each machine
  internet = {
    roles.default.machines."sally-laptop".settings.host  = "192.168.1.10";
    roles.default.machines."fred-laptop".settings.host   = "192.168.1.11";
    roles.default.machines."backup-server".settings.host = "192.168.1.100";
  };

  # SSH on everything
  sshd = {
    roles.server.tags = [ "all" ];
  };

  # WiFi on laptops
  wifi = {
    roles.default.tags = [ "laptop" ];
    roles.default.settings.networks.home = {};
  };

  # One user account per person, on their own machine
  user-sally = {
    module.name = "users";
    roles.default.machines."sally-laptop" = {};
    roles.default.settings.user = "sally";
  };
  user-fred = {
    module.name = "users";
    roles.default.machines."fred-laptop" = {};
    roles.default.settings.user = "fred";
  };

  # Backups: laptops to backup-server, every night at 2 AM
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.client.settings.startAt = "*-*-* 02:00:00";
    roles.server.machines."backup-server" = {};
  };
};
```

When Barb joins the team, add `barb-laptop` with `tags = [ "laptop" ]` and she automatically gets SSH, WiFi, and a backup slot. The inventory scales with you.
