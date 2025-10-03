# Migrating from using `clanModules` to `clanServices`

**Audience**: This is a guide for **people using `clanModules`**.
If you are a **module author** and need to migrate your modules please consult our **new** [clanServices authoring guide](../../guides/services/community.md)

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

### Complex Example: Multi-service Setup

```nix
# Old format
services = {
    borgbackup.production = {
        roles.server.machines = [ "backup-server" ];
        roles.server.config = {
            directory = "/var/backup/borg";
        };
        roles.client.tags = [ "backup" ];
        roles.client.extraModules = [ "nixosModules/borgbackup.nix" ];
    };

    zerotier.company-network = {
        roles.controller.machines = [ "network-controller" ];
        roles.moon.machines = [ "moon-1" "moon-2" ];
        roles.peer.tags = [ "nixos" ];
    };

    sshd.internal = {
        roles.server.tags = [ "nixos" ];
        roles.client.tags = [ "nixos" ];
        config.certificate.searchDomains = [
            "internal.example.com"
            "vpn.example.com"
        ];
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

### Complex Example Migrated

```nix
# New format
instances = {
    borgbackup-production = {
        module = {
            name = "borgbackup";
            input = "clan-core";
        };
        roles.server.machines."backup-server" = { };
        roles.server.settings = {
            directory = "/var/backup/borg";
        };
        roles.client.tags.backup = { };
        roles.client.extraModules = [ ../nixosModules/borgbackup.nix ];
    };

    zerotier-company-network = {
        module = {
            name = "zerotier";
            input = "clan-core";
        };
        roles.controller.machines."network-controller" = { };
        roles.moon.machines."moon-1".settings = {
            stableEndpoints = [ "10.0.0.1" "2001:db8::1" ];
        };
        roles.moon.machines."moon-2".settings = {
            stableEndpoints = [ "10.0.0.2" "2001:db8::2" ];
        };
        roles.peer.tags.nixos = { };
    };

    sshd-internal = {
        module = {
            name = "sshd";
            input = "clan-core";
        };
        roles.server.tags.nixos = { };
        roles.client.tags.nixos = { };
        roles.client.settings = {
            certificate.searchDomains = [
                "internal.example.com"
                "vpn.example.com"
            ];
        };
    };
};
```

---

## Steps to Migrate

### Move `services` entries to `instances`

Check if a service that you use has been migrated [In our reference](../../services/official/index.md)

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

### Add `module.name` and `module.input`

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

### Move role and machine config under `roles`

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

### Important Type Changes

The new `instances` format uses **attribute sets** instead of **lists** for tags and machines:

```nix
# ❌ Old format (lists)
roles.client.tags = [ "backup" ];
roles.server.machines = [ "blob64" ];

# ✅ New format (attribute sets)
roles.client.tags.backup = { };
roles.server.machines.blob64 = { };
```

### Handling Multiple Machines/Tags

When you need to assign multiple machines or tags to a role:

```nix
# ❌ Old format
roles.moon.machines = [ "eva" "eve" ];

# ✅ New format - each machine gets its own attribute
roles.moon.machines.eva = { };
roles.moon.machines.eve = { };
```

---

## Migration Status of clanModules

The following table shows the migration status of each deprecated clanModule:

| clanModule               | Migration Status                                                  | Notes                                                            |
|--------------------------|-------------------------------------------------------------------|------------------------------------------------------------------|
| `admin`                  | ✅ [Migrated](../../services/official/admin.md)              |                                                                  |
| `auto-upgrade`           | ❌ Removed                                                        |                                                                  |
| `borgbackup-static`      | ❌ Removed                                                        |                                                                  |
| `borgbackup`             | ✅ [Migrated](../../services/official/borgbackup.md)         |                                                                  |
| `data-mesher`            | ✅ [Migrated](../../services/official/data-mesher.md)        |                                                                  |
| `deltachat`              | ❌ Removed                                                        |                                                                  |
| `disk-id`                | ❌ Removed                                                        |                                                                  |
| `dyndns`                 | ✅ [Migrated](../../services/official/dyndns.md)             |                                                                  |
| `ergochat`               | ❌ Removed                                                        |                                                                  |
| `garage`                 | ✅ [Migrated](../../services/official/garage.md)             |                                                                  |
| `golem-provider`         | ❌ Removed                                                        |                                                                  |
| `heisenbridge`           | ❌ Removed                                                        |                                                                  |
| `importer`               | ✅ [Migrated](../../services/official/importer.md)           |                                                                  |
| `iwd`                    | ❌ Removed                                                        | Use [wifi service](../../services/official/wifi.md) instead |
| `localbackup`            | ✅ [Migrated](../../services/official/localbackup.md)        |                                                                  |
| `localsend`              | ❌ Removed                                                        |                                                                  |
| `machine-id`             | ✅ [Migrated](../../reference/clan.core/settings.md)              | Now an [option](../../reference/clan.core/settings.md)           |
| `matrix-synapse`         | ✅ [Migrated](../../services/official/matrix-synapse.md)     |                                                                  |
| `moonlight`              | ❌ Removed                                                        |                                                                  |
| `mumble`                 | ❌ Removed                                                        |                                                                  |
| `mycelium`               | ✅ [Migrated](../../services/official/mycelium.md)           |                                                                  |
| `nginx`                  | ❌ Removed                                                        |                                                                  |
| `packages`               | ✅ [Migrated](../../services/official/packages.md)           |                                                                  |
| `postgresql`             | ✅ [Migrated](../../reference/clan.core/settings.md)              | Now an [option](../../reference/clan.core/settings.md)           |
| `root-password`          | ✅ [Migrated](../../services/official/users.md)              | See [migration guide](../../services/official/users.md#migration-from-root-password-module) |
| `single-disk`            | ❌ Removed                                                        |                                                                  |
| `sshd`                   | ✅ [Migrated](../../services/official/sshd.md)               |                                                                  |
| `state-version`          | ✅ [Migrated](../../reference/clan.core/settings.md)              | Now an [option](../../reference/clan.core/settings.md)           |
| `static-hosts`           | ❌ Removed                                                        |                                                                  |
| `sunshine`               | ❌ Removed                                                        |                                                                  |
| `syncthing-static-peers` | ❌ Removed                                                        |                                                                  |
| `syncthing`              | ✅ [Migrated](../../services/official/syncthing.md)          |                                                                  |
| `thelounge`              | ❌ Removed                                                        |                                                                  |
| `trusted-nix-caches`     | ✅ [Migrated](../../services/official/trusted-nix-caches.md) |                                                                  |
| `user-password`          | ✅ [Migrated](../../services/official/users.md)              |                                                                  |
| `vaultwarden`            | ❌ Removed                                                        |                                                                  |
| `xfce`                   | ❌ Removed                                                        |                                                                  |
| `zerotier-static-peers`  | ❌ Removed                                                        |                                                                  |
| `zerotier`               | ✅ [Migrated](../../services/official/zerotier.md)           |                                                                  |
| `zt-tcp-relay`           | ❌ Removed                                                        |                                                                  |

---

!!! Warning
    * Old `clanModules` (`class = "nixos"`) are deprecated and will be removed in the near future.
    * `inventory.services` is no longer recommended; use `inventory.instances` instead.
    * Module authors should begin exporting service modules under the `clan.modules` attribute of their flake.

## Troubleshooting Common Migration Errors

### Error: "not of type `attribute set of (submodule)`"

This error occurs when using lists instead of attribute sets for tags or machines:

```
error: A definition for option `flake.clan.inventory.instances.borgbackup-blob64.roles.client.tags' is not of type `attribute set of (submodule)'.
```

**Solution**: Convert lists to attribute sets as shown in the "Important Type Changes" section above.

### Error: "unsupported attribute `module`"

This error indicates the module structure is incorrect:

```
error: Module ':anon-4:anon-1' has an unsupported attribute `module'.
```

**Solution**: Ensure the `module` attribute has exactly two fields: `name` and `input`.

### Error: "attribute 'pkgs' missing"

This suggests the instance configuration is trying to use imports incorrectly:

```
error: attribute 'pkgs' missing
```

**Solution**: Use the `module = { name = "..."; input = "..."; }` format instead of `imports`.

### Removed Features

The following features from the old `services` format are no longer supported in `instances`:

- Top-level `config` attribute (use `roles.<role>.settings` instead)
- Direct module imports (use the `module` declaration instead)

### extraModules Support

The `extraModules` attribute is still supported in the new instances format! The key change is how modules are specified:

**Old format (string paths relative to clan root):**
```nix
roles.client.extraModules = [ "nixosModules/borgbackup.nix" ];
```

**New format (NixOS modules):**
```nix
# Direct module reference
roles.client.extraModules = [ ../nixosModules/borgbackup.nix ];

# Or using self
roles.client.extraModules = [ self.nixosModules.borgbackup ];

# Or inline module definition
roles.client.extraModules = [
  {
    # Your module configuration here
  }
];
```

The `extraModules` now expects actual **NixOS modules** rather than string paths. This provides better type checking and more flexibility in how modules are specified.

**Alternative: Using @clan/importer**

For scenarios where you need to import modules with specific tag-based targeting, you can also use the dedicated `@clan/importer` service:

```nix
instances = {
  my-importer = {
    module.name = "@clan/importer";
    module.input = "clan-core";
    roles.default.tags.my-tag = { };
    roles.default.extraModules = [ self.nixosModules.myModule ];
  };
};
```

## Further reference

* [Inventory Concept](../../guides/inventory/inventory.md)
* [Authoring a 'clan.service' module](../../guides/services/community.md)
* [ClanServices](../../guides/inventory/clanServices.md)
