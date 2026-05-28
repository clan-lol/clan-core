# Introduction to the Inventory

Imagine you're IT for a small organization: a couple of laptops, a backup server, and a wish to never SSH into the wrong machine again. You want all your laptops to have WiFi configured, your backup server to accept backup connections from the laptops, and a user account for each person on their own machine.

The **inventory** is where you express all of that, and Clan takes care of the rest.

The inventory attribute in the clan.nix file represents your clan's model. It's the record of what machines exist, what services they run, and how everything relates.

---

## The Two-Part Mental Model

The inventory has two main attributes you'll be using:

```nix
inventory = {
  machines = { ... };   # What exists
  instances = { ... };  # What runs on it
};
```

- **machines** is your fleet registry: you name each machine and tell Clan where to find it
- **instances** is your service assignment: you say which services run, and which machines participate in each one

## Machines

Each machine gets a name and some metadata:

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

- **`deploy.targetHost`**: the SSH address Clan uses to deploy to this machine
- **`tags`**: labels you use to group machines (more on this shortly)
- **`machineClass`**: defaults to `"nixos"`. Set it to `"darwin"` for Macs

If you're using the internet networking module, then:

```nix
inventory.instances = {
  internet = {
    roles.default.machines."sally-laptop".settings.host  = "192.168.1.10";
    roles.default.machines."fred-laptop".settings.host   = "192.168.1.11";
    roles.default.machines."backup-server".settings.host = "192.168.1.100";
  };
};
```

Clan builds configurations statically from the inventory, without connecting to machines first. It needs to know the operating system upfront because NixOS and nix-darwin use fundamentally different module systems. Generating the wrong one for a machine would produce a configuration that doesn't work. There is no auto-detection.

For example, suppose Julia has a MacBook:

```nix
inventory.machines = {
  julia-macbook = {
    machineClass = "darwin";
    tags = [ "laptop" ];
  };
};
```

```nix
inventory.instances = {
  internet = {
    roles.default.machines."julia-macbook".settings.host  = "192.168.1.18";
```

## Tags

Tags are labels you apply to machines so you can refer to groups of them by tag name. Instead of saying "WiFi goes on sally-laptop and fred-laptop," you say "WiFi goes on all machines tagged `laptop`."

When you add a new laptop later, just tag it `laptop` and it automatically picks up all the services that target that tag.

Clan defines at least three tags by default:

| Tag | Matches |
|-----|---------|
| `all` | Every machine in your inventory |
| `nixos` | Every machine with `machineClass = "nixos"` |
| `darwin` | Every machine with `machineClass = "darwin"` |

You define the rest by putting them in the `tags` list on each machine, as shown in the example above.

---

## Instances

Clan comes with a library of pre-built services, including things like backups, WiFi, SSH, and user accounts. Each service is a ready-made building block that knows how to configure machines for a specific job. An **instance** is what you get when you put one of those services to work: you pick the service, assign it to machines, and supply whatever settings it needs. Each service defines what roles exist and what those roles do; you decide which machines fill them.

Here's a quick example:

```nix
inventory.instances = {
  wifi = {
    roles.default.tags = [ "laptop" ];
    roles.default.settings.networks.home = {};
  };
};
```

This says: "Run the `wifi` service. Give the `default` role to all machines tagged `laptop`. Configure the `home` network for them."

The instance attribute name (`wifi`) is also the service module name, unless you say otherwise (see [Multiple Instances](#multiple-instances) below).

---

## Roles

When a service runs on multiple machines, each machine may play a different part. A **role** defines what that part is. The `borgbackup` service, for example, needs two kinds of machines: ones that get backed up, and one that stores the backups. It uses roles to tell them apart. Simple services, where every machine does the same job, have just one role called `default`. More involved services define multiple named roles, one for each job that needs doing.

For example, the `borgbackup` service has `client` and `server` roles. Inside clan.nix, you then assign these roles to machines either by name or tag:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.tags = [ "laptop" ];             # Laptops get backed up
    roles.server.machines."backup-server" = {};   # backup-server stores the backups
  };
};
```

The above code uses both tags and names:

- **By tag**: `roles.client.tags = [ "laptop" ]` — resolves to all machines with that tag
- **By name**: `roles.server.machines."backup-server" = {}` — pinpoints a specific machine

You can also combine both approaches within the same role. If most of your backup clients are laptops but you also want to include one specific desktop, list both in the same role; Clan gathers all the machines from the tags and the names and treats them as one group.

```nix
inventory.instances = {
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.client.machines."office-desktop" = {};   # Also back up this specific machine
    roles.server.machines."backup-server" = {};
  };
};
```

## Settings

Services are configurable through the settings attribute, which you find per role. Settings can apply to all machines in a role, or be overridden per machine.

**Role-wide settings**: everyone in this role gets this:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.client.settings.startAt = "*-*-* 02:00:00";   # All clients back up at 2 AM
    roles.server.machines."backup-server" = {};
  };
};
```

**Per-machine settings**: one machine gets something extra:

```nix
inventory.instances = {
  wifi = {
    roles.default.settings.networks.home = {};   # Everyone gets home WiFi
    roles.default.machines."sally-laptop" = {
      settings.networks.office = {};             # Sally also gets office WiFi
    };
    roles.default.machines."fred-laptop" = {};   # Fred uses the role-wide settings as-is
  };
};
```

A quick note on `= {}`: in these examples you will see many attributes assigned to an empty set. In Nix, this is how you say "include this, but I have nothing extra to specify." When you write `roles.default.machines."fred-laptop" = {}`, you are adding Fred's laptop to the role with no per-machine customization; it will receive whatever the role provides and nothing more. When you write `settings.networks.home = {}`, you are enabling that network with its default settings. The key being present is the declaration; the empty braces mean there is nothing to add.

Per-machine settings are merged on top of role-wide settings, so you only need to specify what's different. The WiFi example above illustrates this: the role provides the `home` network to every laptop. Sally's entry adds `office` on top of that; she ends up with both. Fred's entry is empty, so he gets only what the role provides. You never repeat the role-wide settings for each machine; Clan applies them as the baseline and layers any per-machine additions on top.

Here is how that looks if a third laptop needs access to additional networks:

```nix
inventory.instances = {
  wifi = {
    roles.default.settings.networks.home = {};      # All laptops get home WiFi
    roles.default.machines."sally-laptop" = {
      settings.networks.office = {};                # Sally also gets office WiFi
    };
    roles.default.machines."fred-laptop" = {
      settings.networks.office = {};                # Fred gets office WiFi
      settings.networks.guest = {};                 # Fred also gets the guest network
    };
  };
};
```

Sally ends up with `home` and `office`. Fred ends up with `home`, `office`, and `guest`. Neither needs to specify `home` again; the role already covers it.

---

## Multiple Instances

Sometimes you need the same service configured differently for different machines. The `users` service is a good example: each person needs their own account, with their own username, on their own machine. You can't declare two things both named `users`, but you can create two separately named instances that both use the `users` service module.

By default, the instance attribute name is also the service module name. But you can run the same service multiple times by giving each instance its own name and setting `module.name`:

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

The `module.name` field tells Clan which service module to use. You can name the instances whatever makes sense; they just can't share a name.

> **Note:** Not every service supports multiple instances. Check the service documentation before setting up more than one.

## Putting It All Together

Here's the scenario from the intro, fully wired up, using the dotted style you'll see in most `clan.nix` files:

```nix
inventory.machines = {
  sally-laptop = {
    deploy.targetHost = "root@192.168.1.10";
    tags = [ "laptop" ];
  };
  fred-laptop = {
    deploy.targetHost = "root@192.168.1.11";
    tags = [ "laptop" ];
  };
  backup-server = {
    deploy.targetHost = "root@192.168.1.100";
    tags = [ "server" ];
  };
};

inventory.instances = {
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

  # Backups: laptops → backup-server, every night at 2 AM
  borgbackup = {
    roles.client.tags = [ "laptop" ];
    roles.client.settings.startAt = "*-*-* 02:00:00";
    roles.server.machines."backup-server" = {};
  };
};
```

When Barb joins the team, you add `barb-laptop` with `tags = [ "laptop" ]` and she automatically gets SSH, WiFi, and a backup slot. The inventory scales with you.
