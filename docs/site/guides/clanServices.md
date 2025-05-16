# Using `clanServices`

Clan’s `clanServices` system is a composable way to define and deploy services across machines. It replaces the legacy `clanModules` approach and introduces better structure, flexibility, and reuse.

This guide shows how to **instantiate** a `clanService`, explains how service definitions are structured in your inventory, and how to pick or create services from modules exposed by flakes.

The term **Multi-host-modules** was introduced previously in the [nixus repository](https://github.com/infinisil/nixus) and represents a similar concept.

---

## Overview

A `clanService` is used in:

```nix
inventory.instances.<instance_name>
```

Each instance includes a reference to a **module specification** — this is how Clan knows which service module to use and where it came from.
You can reference services from any flake input, allowing you to compose services from multiple flake sources.

These operate on a strict *role-based membership model*, meaning machines are added by assigning them specific *roles*.

---

## Basic Example

Example of instantiating a `borgbackup` service using `clan-core`:

```nix
inventory.instances = {
    # Arbitrary unique name for this 'borgbackup' instance
    borgbackup-example = {
        module =  {
            name = "borgbackup";  # <-- Name of the module
            input = "clan-core"; # <-- The flake input where the service is defined
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

🔗 Learn how to write your own service: [Authoring a clanService](../guides/authoring/clanServices/index.md)

You might expose your service module from your flake — this makes it easy for other people to also use your module in their clan.

---

## 💡 Tips for Working with clanServices

* You can add multiple inputs to your flake (`clan-core`, `your-org-modules`, etc.) to mix and match services.
* Each service instance is isolated by its key in `inventory.instances`, allowing you to deploy multiple versions or roles of the same service type.
* Roles can target different machines or be scoped dynamically.

---

## What’s Next?

* [Author your own clanService →](../guides/authoring/clanServices/index.md)
* [Migrate from clanModules →](../guides/migrate-inventory-services.md)
<!-- TODO: * [Understand the architecture →](../explanation/clan-architecture.md) -->
