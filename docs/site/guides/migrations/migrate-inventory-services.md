# Migrate Inventory Services

## Migrating from using `clanModules` to `clanServices`

**Audience**: This is a guide for **people using `clanModules`**.
If you are a **module author** and need to migrate your modules please consult our **new** [clanServices authoring guide](/docs/guides/services/community)

### What's Changing?

Clan is transitioning from the legacy `clanModules` system to the `clanServices` system. The sections below show how to migrate your service definitions from the old format (`inventory.services`) to the new format (`inventory.instances`).

| Feature          | `clanModules` (Old)        | `clanServices` (New)    |
| ---------------- | -------------------------- | ----------------------- |
| Module Class     | `"nixos"`                  | `"clan.service"`        |
| Inventory Key    | `services`                 | `instances`             |
| Module Source    | Static                     | Composable via flakes   |
| Custom Settings  | Loosely structured         | Strongly typed per-role |
| Migration Status | Deprecated (to be removed) | ✅ Preferred             |

---

### Before: Old `services` Definition

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

#### Complex Example: Multi-service Setup

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

### After: New `instances` Definition with `clanServices`

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

#### Complex Example Migrated

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
        roles.client.tags = [ "backup" ];
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
        roles.peer.tags = [ "nixos" ];
    };

    sshd-internal = {
        module = {
            name = "sshd";
            input = "clan-core";
        };
        roles.server.tags = [ "nixos" ];
        roles.client.tags = [ "nixos" ];
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

### Steps to Migrate

#### Move `services` entries to `instances`

Check if a service that you use has been migrated [In our reference](/docs/services/definition)

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

#### Add `module.name` and `module.input`

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

#### Move role and machine config under `roles`

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

#### Important Type Changes

The new `instances` format uses **attribute sets** instead of **lists** for tags and machines:

```nix
roles.client.tags = [ "backup" ];
# Old format (lists)
roles.server.machines = [ "blob64" ];

# New format (attribute sets)
roles.server.machines.blob64 = { };

# Tags stay lists
roles.client.tags = [ "backup" ];
```

#### Handling Multiple Machines/Tags

When you need to assign multiple machines or tags to a role:

```nix
# Old format
roles.moon.machines = [ "eva" "eve" ];

# New format - each machine gets its own attribute
roles.moon.machines.eva = { };
roles.moon.machines.eve = { };
```

---

### Migration Status of clanModules

Below is the migration status of each deprecated clanModule:

| clanModule               | Migration Status                                                  | Notes                                                            |
|--------------------------|-------------------------------------------------------------------|------------------------------------------------------------------|
| `admin`                  | ✅ [Migrated](/docs/services/official/admin)              |                                                                  |
| `auto-upgrade`           | ❌ Removed                                                        |                                                                  |
| `borgbackup-static`      | ❌ Removed                                                        |                                                                  |
| `borgbackup`             | ✅ [Migrated](/docs/services/official/borgbackup)         |                                                                  |
| `data-mesher`            | ✅ [Migrated](/docs/services/official/data-mesher)        |                                                                  |
| `deltachat`              | ❌ Removed                                                        |                                                                  |
| `disk-id`                | ❌ Removed                                                        |                                                                  |
| `dyndns`                 | ✅ [Migrated](/docs/services/official/dyndns)             |                                                                  |
| `ergochat`               | ❌ Removed                                                        |                                                                  |
| `garage`                 | ✅ [Migrated](/docs/services/official/garage)             |                                                                  |
| `golem-provider`         | ❌ Removed                                                        |                                                                  |
| `heisenbridge`           | ❌ Removed                                                        |                                                                  |
| `importer`               | ✅ [Migrated](/docs/services/official/importer)           |                                                                  |
| `iwd`                    | ❌ Removed                                                        | Use [wifi service](/docs/services/official/wifi) instead |
| `localbackup`            | ✅ [Migrated](/docs/services/official/localbackup)        |                                                                  |
| `localsend`              | ❌ Removed                                                        |                                                                  |
| `machine-id`             | ✅ [Migrated](/docs/reference/clan.core/settings)              | Now an [option](/docs/reference/clan.core/settings)           |
| `matrix-synapse`         | ✅ [Migrated](/docs/services/official/matrix-synapse)     |                                                                  |
| `moonlight`              | ❌ Removed                                                        |                                                                  |
| `mumble`                 | ❌ Removed                                                        |                                                                  |
| `mycelium`               | ✅ [Migrated](/docs/services/official/mycelium)           |                                                                  |
| `nginx`                  | ❌ Removed                                                        |                                                                  |
| `packages`               | ✅ [Migrated](/docs/services/official/packages)           |                                                                  |
| `postgresql`             | ✅ [Migrated](/docs/reference/clan.core/settings)              | Now an [option](/docs/reference/clan.core/settings)           |
| `root-password`          | ✅ [Migrated](/docs/services/official/users)              | See [migration guide](/docs/services/official/users#migration-from-root-password-module) |
| `single-disk`            | ❌ Removed                                                        |                                                                  |
| `sshd`                   | ✅ [Migrated](/docs/services/official/sshd)               |                                                                  |
| `state-version`          | ✅ [Migrated](/docs/reference/clan.core/settings)              | Now an [option](/docs/reference/clan.core/settings)           |
| `static-hosts`           | ❌ Removed                                                        |                                                                  |
| `sunshine`               | ❌ Removed                                                        |                                                                  |
| `syncthing-static-peers` | ❌ Removed                                                        |                                                                  |
| `syncthing`              | ✅ [Migrated](/docs/services/official/syncthing)          |                                                                  |
| `thelounge`              | ❌ Removed                                                        |                                                                  |
| `trusted-nix-caches`     | ✅ [Migrated](/docs/services/official/trusted-nix-caches) |                                                                  |
| `user-password`          | ✅ [Migrated](/docs/services/official/users)              |                                                                  |
| `vaultwarden`            | ❌ Removed                                                        |                                                                  |
| `xfce`                   | ❌ Removed                                                        |                                                                  |
| `zerotier-static-peers`  | ❌ Removed                                                        |                                                                  |
| `zerotier`               | ✅ [Migrated](/docs/services/official/zerotier)           |                                                                  |
| `zt-tcp-relay`           | ❌ Removed                                                        |                                                                  |

---

:::admonition[Warning]{type=warning}

* Old `clanModules` (`class = "nixos"`) are deprecated and will be removed in the near future.
* `inventory.services` is no longer recommended; use `inventory.instances` instead.
* Module authors should begin exporting service modules under the `clan.modules` attribute of their flake.
:::

### Troubleshooting Common Migration Errors

#### Error: "not of type `attribute set of (submodule)`"

Appears when using lists instead of attribute sets for tags or machines:

```text
error: A definition for option `flake.clan.inventory.instances.borgbackup-blob64.roles.client.tags' is not of type `attribute set of (submodule)'.
```

**Solution**: Convert lists to attribute sets as shown in the "Important Type Changes" section above.

#### Error: "unsupported attribute `module`"

Indicates the module structure is incorrect:

```text
error: Module ':anon-4:anon-1' has an unsupported attribute `module'.
```

**Solution**: Ensure the `module` attribute has exactly two fields: `name` and `input`.

#### Error: "attribute 'pkgs' missing"

Suggests the instance configuration is trying to use imports incorrectly:

```text
error: attribute 'pkgs' missing
```

**Solution**: Use the `module = { name = "..."; input = "..."; }` format instead of `imports`.

#### Removed Features

The following features from the old `services` format are no longer supported in `instances`:

* Top-level `config` attribute (use `roles.<role>.settings` instead)
* Direct module imports (use the `module` declaration instead)

#### extraModules Support

The `extraModules` attribute is still supported in the new instances format! The key change is how modules are specified:

**Old format (string paths relative to Clan root):**

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

The `extraModules` option now expects actual **NixOS modules** rather than string paths, giving you better type checking and more flexibility in how modules are specified.

**Alternative: Using @clan/importer**

For scenarios where you need to import modules with specific tag-based targeting, you can also use the dedicated `@clan/importer` service:

```nix
instances = {
  my-importer = {
    module.name = "@clan/importer";
    module.input = "clan-core";
    roles.default.tags = [ "my-tag" ];
    roles.default.extraModules = [ self.nixosModules.myModule ];
  };
};
```

### Further reference

* [Inventory Concept](/docs/guides/inventory/intro-to-inventory)
* [Authoring a 'clan.service' module](/docs/guides/services/community)
* [ClanServices](/docs/guides/services/intro-to-services-revised)
