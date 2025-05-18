# Migrating from using `clanModules` to `clanServices`

**Audience**: This is a guide for **people using `clanModules`**.
If you are a **module author** and need to migrate your modules please consult our **new** [clanServices authoring guide](../authoring/clanServices/index.md)

## What's Changing?

Clan is transitioning from the legacy `clanModules` system to the `clanServices` system. This guide will help you migrate your service definitions from the old format (`inventory.services`) to the new format (`inventory.instances`).

| Feature          | `clanModules` (Old)        | `clanServices` (New)    |
| ---------------- | -------------------------- | ----------------------- |
| Module Class     | `"nixos"`                  | `"clan.service"`        |
| Inventory Key    | `services`                 | `instances`             |
| Module Source    | Static                     | Composable via flakes   |
| Custom Settings  | Loosely structured         | Strongly typed per-role |
| Migration Status | Deprecated (to be removed) | ✅ Preferred             |

---

## Before: Old `services` Definition

```nix
services = {
    admin = {
        simple = {
            roles.default.tags = [ "all" ];

            roles.default.config = {
                allowedKeys = {
                    "key-1" = "ssh-ed25519 AAAA...0J jon@jon-os";
                };
            };
        };
    };
};
```

---

## ✅ After: New `instances` Definition with `clanServices`

```nix
instances = {
    # The instance_name is arbitrary but must be unique
    # We recommend to incorporate the module name in some kind to keep it clear
    admin-simple = {
        module = {
            name = "admin";
            input = "clan-core";
        };

        roles.default.tags."all" = {};

        # Move settings either into the desired role
        # In that case they effect all 'client-machines'
        roles.default.settings = {
            allowedKeys = {
                "key-1" = "ssh-ed25519 AAAA...0J jon@jon-os";
            };
        };
        # ----------------------------
        # OR move settings into the machine
        # then they affect only that single 'machine'
        roles.default.machines."jon".settings = {
            allowedKeys = {
                "key-1" = "ssh-ed25519 AAAA...0J jon@jon-os";
            };
        };
    };
};
```

---

## Steps to Migrate



### 1. Move `services` entries to `instances`

Check if a service that you use has been migrated [In our reference](../../reference/clanServices/index.md)

In your inventory, move it from:

```nix
services = { ... };
```

to:

```nix
instances = { ... };
```

Each nested service-instance-pair becomes a flat key, like `borgbackup.simple → borgbackup-simple`.

---

### 2. Add `module.name` and `module.input`

Each instance must declare the module name and flake input it comes from:

```nix
module = {
  name = "borgbackup";
  input = "clan-core";  # The name of your flake input
};
```

If you used `clan-core` as an input:

```nix
inputs.clan-core.url = "github:clan/clan-core";
```

Then refer to it as `input = "clan-core"`.

---

### 3. Move role and machine config under `roles`

In the new system:

* Use `roles.<role>.machines.<hostname>.settings` for machine-specific config.
* Use `roles.<role>.settings` for role-wide config.
* Remove: `.config` as a top-level attribute is removed.

Example:

```nix
roles.default.machines."test-inventory-machine".settings = {
  packages = [ "hello" ];
};
```

---

!!! Warning
    * Old `clanModules` (`class = "nixos"`) are deprecated and will be removed in the near future.
    * `inventory.services` is no longer recommended; use `inventory.instances` instead.
    * Module authors should begin exporting service modules under the `clan.modules` attribute of their flake.

## Further reference

* [Authoring a 'clan.service' module](../authoring/clanServices/index.md)
* [ClanServices](../clanServices.md)
* [Inventory Reference](../../reference/nix-api/inventory.md)