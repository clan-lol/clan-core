# Using `clanServices`

Clan’s `clanServices` system is a composable way to define and deploy services across machines. It replaces the legacy `clanModules` approach and introduces better structure, flexibility, and reuse.

This guide shows how to **instantiate** a `clanService`, explains how service definitions are structured in your inventory, and how to pick or create services from modules exposed by flakes.

---

## Overview

A `clanService` is used in:

```nix
inventory.instances.<instance_name>
```

Each instance includes a reference to a **module specification** — this is how Clan knows which service module to use and where it came from.
You can reference services from any flake input, allowing you to compose services from multiple flake sources.

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

## Picking a clanService

You can use services exposed by Clan’s core module library, `clan-core`.

🔗 See: [List of Available Services in clan-core](../reference/clanServices/index.md)

## Defining Your Own Service

You can also author your own `clanService` modules.

🔗 Learn how to write your own service: [Authoring a clanService](../authoring/clanServices/index.md)

You might expose your service module from your flake — this makes it easy for other people to also use your module in their clan.

---

## 💡 Tips for Working with clanServices

* You can add multiple inputs to your flake (`clan-core`, `your-org-modules`, etc.) to mix and match services.
* Each service instance is isolated by its key in `inventory.instances`, allowing you to deploy multiple versions or roles of the same service type.
* Roles can target different machines or be scoped dynamically.

---

## What’s Next?

* [Author your own clanService →](../authoring/clanServices/index.md)
* [Migrate from clanModules →](../guides/migrate-inventory-services.md)
<!-- TODO: * [Understand the architecture →](../explanation/clan-architecture.md) -->
