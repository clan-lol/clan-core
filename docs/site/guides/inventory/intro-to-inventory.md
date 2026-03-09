# Introduction to the Inventory

The **inventory** is the central registry of your clan. It's where you declare what machines exist and what services they run.

---

## The Shape of the Inventory

For clarity, we'll write the inventory as a single nested block. In practice, you'll often see the dotted style (`inventory.machines = ...`) which is equivalent.

```nix
inventory = {

  machines = {
    # Define your machines here
  };

  instances = {
    # Define your service instances here
  };

};
```

We have two sections:
- **machines**: "what machines exists"
- **instances**: "what the machines run"

---

## Defining Machines

Each machine gets a name and some metadata. For example, here we're creating three machines and specifying what IP address Clan can find them at; we're also applying some tags to them.

```nix
inventory = {
  machines = {

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
};
```

- **deploy.targetHost**: where Clan SSHes to deploy this machine
- **tags**: labels for grouping machines (more on this below)

---

## Defining Service Instances

An **instance** is a configured service. You add instances to `inventory.instances`:

```nix
inventory = {
  instances = {

    wifi = {
      roles.default.tags.laptop = {};
      roles.default.settings.networks.home = {};
    };

  };
};
```

This says: "Create an instance of the `wifi` service. Assign all machines tagged `laptop` to the default role. Configure the `home` network."

---

## The Module: Which Service to Use

If you only need one instance of a service, you can just use the service name as the attribute name as with the `wifi` service above.

But if you need multiple instances of the service, you can give each its own name, and set the `module.name` attribute, like so:

```nix
instances = {
  user-sally = {
    module.name = "users";   # This instance uses the "users" service
    roles.default.machines."sally-laptop" = {};
    roles.default.settings.user = "sally";
  };

  user-fred = {
    module.name = "users";   # Another instance of the same service
    roles.default.machines."fred-laptop" = {};
    roles.default.settings.user = "fred";
  };
};
```

This lets you have **multiple instances** of the same service. You can't have two things named `users`, but you can have `user-sally` and `user-fred` both using the `users` module.

---

## Roles: What Job Does Each Machine Play?

A **role** defines what part a machine plays within a service.

**Simple services** have just one role called `default`:

```nix
wifi = {
  roles.default.tags.laptop = {};
};
```

This means all machines that have the tag `laptop` will receive this service.

**Multi-role services** have distinct jobs. For example, the `borgbackup` service has `client` and `server` roles:

```nix
borgbackup = {
  roles.client.machines."sally-laptop" = {};   # Gets backed up
  roles.client.machines."fred-laptop" = {};    # Gets backed up
  roles.server.machines."backup-server" = {};  # Stores the backups
};
```

The service itself defines what roles exist; you then assign machines to them. If the docs say a service has roles `a`, `b`, and `c`, you can use:

```nix
roles.a.machines."my-machine" = {};
roles.b.tags.laptop = {};
roles.c.tags.all = {};
```

---

## Tags: Grouping Machines

A **tag** is a label you attach to machines so you can reference them as a group.

Think of it like labeling boxes when you move. You might labl some "kitchen," some "bedroom." Then when you want something in all kitchen boxes, you just look for that label.

### The Automatic `all` Tag

Every machine automatically has the `all` tag:

```nix
roles.default.tags.all = {};   # Applies to every machine
```

### Custom Tags

You define custom tags on your machines, like so:

```nix
machines = {
  sally-laptop.tags = [ "laptop" ];
  fred-laptop.tags = [ "laptop" ];
  backup-server.tags = [ "server" ];
};
```

Then reference them in services:

```nix
instances = {
  wifi = {
    roles.default.tags.laptop = {};   # Only laptops get WiFi
  };

  packages = {
    roles.default.tags.server.settings = {
      packages = [ "nginx" "postgresql" ];   # Only servers get these
    };
  };
};
```

When you add a new laptop, just tag it `laptop` and it automatically gets all laptop services. No need to add it to each service individually.

---

## Settings: Configuring Services

Most services have configurable settings. Settings can be applied:

**Per role** (affects all machines with that role):

```nix
borgbackup = {
  roles.client.tags.all = {};
  roles.client.settings = {
    startAt = "*-*-* 02:00:00";   # All clients backup at 2 AM
  };
  roles.server.machines."backup-server" = {};
};
```

**Per machine** (affects only that specific machine):

```nix
wifi = {
  roles.default.machines."sally-laptop" = {
    settings.networks.home = {};
    settings.networks.office = {};   # Sally also connects to office WiFi
  };
  roles.default.machines."fred-laptop" = {
    settings.networks.home = {};     # Fred only needs home WiFi
  };
};
```

Note: inside a machine assignment, it's always `settings`. An empty `= {}` means "assign this machine to the role, using role-wide settings." If you need per-machine customization, put `settings` inside the braces, as shown in the following example under "Putting It All Together."

---

## Putting It All Together

Here's a complete example using the dotted style you'll see in most `clan.nix` files:

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
  # SSH on all machines
  sshd = {
    roles.server.tags.all = {};
  };

  # WiFi on laptops only
  wifi = {
    roles.default.tags.laptop = {};
    roles.default.settings.networks.home = {};
  };

  # User accounts
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

  # Backups
  borgbackup = {
    roles.client.tags.laptop = {};
    roles.server.machines."backup-server" = {};
  };
};
```

---

## Advanced: Multiple Instances of the Same Service

Sometimes you need the same service configured in different ways. For example, you might want your backup server to also be backed up to a different server.

```nix
instances = {

  # First backup instance: laptops back up to the NAS
  backup-to-nas = {
    module.name = "borgbackup";
    roles.client.tags.laptop = {};
    roles.server.machines."nas" = {};
  };

  # Second backup instance: the NAS backs up to offsite storage
  offsite-backup = {
    module.name = "borgbackup";
    roles.client.machines."nas" = {};        # NAS is a client here
    roles.server.machines."offsite" = {};
  };

};
```

In this setup:
- Laptops back up to the NAS
- The NAS backs up to an offsite server
- The NAS plays `server` in one instance and `client` in another

Each instance is independent: different name, different role assignments, different settings if needed.

**Warning:** Not all services support multiple instances. Check the service documentation before creating multiple instances of the same service.
