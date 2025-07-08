# How to Set `targetHost` for a Machine

The `targetHost` defines where the machine can be reached for operations like SSH or deployment. You can set it in two ways, depending on your use case.

---

## ✅ Option 1: Use the Inventory (Recommended for Static Hosts)

If the hostname is **static**, like `server.example.com`, set it in the **inventory**:

```{.nix title="flake.nix" hl_lines="8"}
{
  # edlided
  outputs =
    { self, clan-core, ... }:
    let
      # Sometimes this attribute set is defined in clan.nix
      clan = clan-core.lib.clan {
        inventory.machines.jon = {
            deploy.targetHost = "root@server.example.com";
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
      # elided
    };
}
```

This is fast, simple and explicit, and doesn’t require evaluating the NixOS config. We can also displayed it in the clan-cli or clan-app.

---

## ✅ Option 2: Use NixOS (Only for Dynamic Hosts)

If your target host depends on a **dynamic expression** (like using the machine’s evaluated FQDN), set it inside the NixOS module:

```{.nix title="flake.nix" hl_lines="8"}
{
  # edlided
  outputs =
    { self, clan-core, ... }:
    let
      # Sometimes this attribute set is defined in clan.nix
      clan = clan-core.lib.clan {
        machines.jon = {config, ...}: {
            clan.core.networking.targetHost = "jon@${config.networking.fqdn}";
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
      # elided
    };
}
```

Use this **only if the value cannot be made static**, because it’s slower and won't be displayed in the clan-cli or clan-app yet.

---

## 📝 TL;DR

| Use Case                  | Use Inventory? | Example                          |
| ------------------------- | -------------- | -------------------------------- |
| Static hostname           | ✅ Yes          | `root@server.example.com`        |
| Dynamic config expression | ❌ No           | `jon@${config.networking.fqdn}` |

---

## 🚀 Coming Soon: Unified Networking Module

We’re working on a new networking module that will automatically do all of this for you.

- Easier to use
- Sane defaults: You’ll always be able to reach the machine — no need to worry about hostnames.
- ✨ Migration from **either method** will be supported and simple.

## Summary

- Ask: *Does this hostname dynamically change based on NixOS config?*
- If **no**, use the inventory.
- If **yes**, then use NixOS config.
