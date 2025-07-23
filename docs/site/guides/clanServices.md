# Using `clanServices`

Clan’s `clanServices` system is a composable way to define and deploy services across machines.

This guide shows how to **instantiate** a `clanService`, explains how service definitions are structured in your inventory, and how to pick or create services from modules exposed by flakes.

The term **Multi-host-modules** was introduced previously in the [nixus repository](https://github.com/infinisil/nixus) and represents a similar concept.

---

## Overview

Services are used in `inventory.instances`, and then they attach to *roles* and *machines* — meaning you decide which machines run which part of the service.

For example:

```nix
inventory.instances = {
  borgbackup = {
    roles.client.machines."laptop" = {};
    roles.client.machines."server1" = {};

    roles.server.machines."backup-box" = {};
  };
}
```

This says: “Run borgbackup as a *client* on my *laptop* and *server1*, and as a *server* on *backup-box*.”

## Module source specification

Each instance includes a reference to a **module specification** — this is how Clan knows which service module to use and where it came from.
Usually one would just use `imports` but we needd to make the `module source` configurable via Python API.
By default it is not required to specify the `module`, in which case it defaults to the preprovided services of clan-core.

---

## Override Example

Example of instantiating a `borgbackup` service using `clan-core`:

```nix
inventory.instances = {
    # Instance Name: Different name for this 'borgbackup' instance
    borgbackup = {
        # Since this is instances."borgbackup" the whole `module = { ... }` below is equivalent and optional.
        module =  {
            name = "borgbackup";  # <-- Name of the module (optional)
            input = "clan-core"; # <-- The flake input where the service is defined (optional)
        };
        # Participation of the machines is defined via roles
        # Right side needs to be an attribute set. Its purpose will become clear later
        roles.client.machines."machine-a" = {};
        roles.server.machines."backup-host" = {};
    };
}
```

If you used `clan-core` as an input attribute for your flake:

```nix
      # ↓ module.input = "clan-core"
inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core"
```

## Simplified Example

If only one instance is needed for a service and the service is a clan core service, the `module` definition can be omitted.

```nix
# Simplified way of specifying a single instance
inventory.instances = {
    # instance name is `borgbackup` -> clan core module `borgbackup` will be loaded.
    borgbackup = {
        # Participation of the machines is defined via roles
        # Right side needs to be an attribute set. Its purpose will become clear later
        roles.client.machines."machine-a" = {};
        roles.server.machines."backup-host" = {};
    };
}
```

## Configuration Example

Each role might expose configurable options

See clan's [clanServices reference](../reference/clanServices/index.md) for available options

```nix
inventory.instances = {
    borgbackup-example = {
        module =  {
            name = "borgbackup";
            input = "clan-core";
        };
        roles.client.machines."machine-a" = {
            # 'client' -Settings of 'machine-a'
            settings = {
                backupFolders = [
                    /home
                    /var
                ];
            };
            # ---------------------------
        };
        roles.server.machines."backup-host" = {};
    };
}
```

## Tags

Multiple members can be defined using tags as follows

```nix
inventory.instances = {
    borgbackup-example = {
        module =  {
            name = "borgbackup";
            input = "clan-core";
        };
        #
        # The 'all' -tag targets all machines
        roles.client.tags."all" = {};
        # ---------------------------
        roles.server.machines."backup-host" = {};
    };
}
```

## Picking a clanService

You can use services exposed by Clan’s core module library, `clan-core`.

🔗 See: [List of Available Services in clan-core](../reference/clanServices/index.md)

## Defining Your Own Service

You can also author your own `clanService` modules.

🔗 Learn how to write your own service: [Authoring a clanService](../developer/extensions/clanServices/index.md)

You might expose your service module from your flake — this makes it easy for other people to also use your module in their clan.

---

## 💡 Tips for Working with clanServices

* You can add multiple inputs to your flake (`clan-core`, `your-org-modules`, etc.) to mix and match services.
* Each service instance is isolated by its key in `inventory.instances`, allowing you to deploy multiple versions or roles of the same service type.
* Roles can target different machines or be scoped dynamically.

---

## What’s Next?

* [Author your own clanService →](../developer/extensions/clanServices/index.md)
* [Migrate from clanModules →](../guides/migrations/migrate-inventory-services.md)
<!-- TODO: * [Understand the architecture →](../explanation/clan-architecture.md) -->
