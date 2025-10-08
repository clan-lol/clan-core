# Connecting to Your Machines

Clan provides automatic networking with fallback mechanisms to reliably connect to your machines.

## Option 1: Automatic Networking with Fallback (Recommended)

Clan's networking module automatically manages connections through various network technologies with intelligent fallback. When you run `clan ssh` or `clan machines update`, Clan tries each configured network by priority until one succeeds.

### Basic Setup with Internet Service

For machines with public IPs or DNS names, use the `internet` service to configure direct SSH while keeping fallback options:

```{.nix title="flake.nix" hl_lines="7-10 14-16"}
{
  outputs = { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan {
        inventory.instances = {
          # Direct SSH with fallback support
          internet = {
            roles.default.machines.server1 = {
              settings.host = "server1.example.com";
            };
            roles.default.machines.server2 = {
              settings.host = "192.168.1.100";
            };
          };

          # Fallback: Secure connections via Tor
          tor = {
            roles.server.tags.nixos = { };
          };
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations;
    };
}
```

### Advanced Setup with Multiple Networks

```{.nix title="flake.nix" hl_lines="7-10 13-16 19-21"}
{
  outputs = { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan {
        inventory.instances = {
          # Priority 1: Try direct connection first
          internet = {
            roles.default.machines.publicserver = {
              settings.host = "public.example.com";
            };
          };

          # Priority 2: VPN for internal machines
          zerotier = {
            roles.controller.machines."controller" = { };
            roles.peer.tags.nixos = { };
          };

          # Priority 3: Tor as universal fallback
          tor = {
            roles.server.tags.nixos = { };
          };
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations;
    };
}
```

### How It Works

Clan automatically tries networks in order of priority:
1. Direct internet connections (if configured)
2. VPN networks (ZeroTier, Tailscale, etc.)
3. Tor hidden services
4. Any other configured networks

If one network fails, Clan automatically tries the next.

### Useful Commands

```bash
# View all configured networks and their status
clan network list

# Test connectivity through all networks
clan network ping machine1

# Show complete network topology
clan network overview
```

## Option 2: Manual targetHost (Bypasses Fallback!)

!!! warning
    Setting `targetHost` directly **disables all automatic networking and fallback**. Only use this if you need complete control and don't want Clan's intelligent connection management.

### Using Inventory (For Static Addresses)

Use inventory-level `targetHost` when the address is **static** and doesn't depend on NixOS configuration:

```{.nix title="flake.nix" hl_lines="8"}
{
  outputs = { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan {
        inventory.machines.server = {
          # WARNING: This bypasses all networking modules!
          # Use for: Static IPs, DNS names, known hostnames
          deploy.targetHost = "root@192.168.1.100";
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations;
    };
}
```

**When to use inventory-level:**
- Static IP addresses: `"root@192.168.1.100"`
- DNS names: `"user@server.example.com"`
- Any address that doesn't change based on machine configuration

### Using NixOS Configuration (For Dynamic Addresses)

Use machine-level `targetHost` when you need to **interpolate values from the NixOS configuration**:

```{.nix title="flake.nix" hl_lines="7"}
{
  outputs = { self, clan-core, ... }:
    let
      clan = clan-core.lib.clan {
        machines.server = { config, ... }: {
          # WARNING: This also bypasses all networking modules!
          # REQUIRED for: Addresses that depend on NixOS config
          clan.core.networking.targetHost = "root@${config.networking.hostName}.local";
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations;
    };
}
```

**When to use machine-level (NixOS config):**
- Using hostName from config: `"root@${config.networking.hostName}.local"`
- Building from multiple config values: `"${config.users.users.deploy.name}@${config.networking.hostName}"`
- Any address that depends on evaluated NixOS configuration

!!! info "Key Difference"
    **Inventory-level** (`deploy.targetHost`) is evaluated immediately and works with static strings.
    **Machine-level** (`clan.core.networking.targetHost`) is evaluated after NixOS configuration and can access `config.*` values.

## Quick Decision Guide

| Scenario | Recommended Approach | Why |
|----------|---------------------|-----|
| Public servers | `internet` service | Keeps fallback options |
| Mixed infrastructure | Multiple networks | Automatic failover |
| Machines behind NAT | ZeroTier/Tor | NAT traversal with fallback |
| Testing/debugging | Manual targetHost | Full control, no magic |
| Single static machine | Manual targetHost | Simple, no overhead |

## Command-Line Override

The `--target-host` flag bypasses ALL networking configuration:

```bash
# Emergency access - ignores all networking config
clan machines update server --target-host root@backup-ip.com

# Direct SSH - no fallback attempted
clan ssh laptop --target-host user@10.0.0.5
```

Use this for debugging or emergency access when automatic networking isn't working.
