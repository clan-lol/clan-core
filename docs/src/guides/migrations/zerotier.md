# ZeroTier: migrate to multi-instance

## Manual ZeroTier upgrade from <=25.11 to >=26.05

## Before you start

- **Upgrade one non-critical machine first.** Pick a machine whose loss of
  connectivity will not lock you out, and make sure you have an SSH fallback
  that does **not** go over ZeroTier.
- **Keep config changes minimal.** If your network worked before the bump, do
  not rewrite your inventory.

    The only edits required are the ones in [Required config updates](#required-config-updates-if-you-referenced-the-old-generator)
    below, and only if they apply to you.

## What changed

### Multi-instance

A machine can now join several ZeroTier networks. Each network is a single
`inventory.instances.<name>` entry with `module.name = "zerotier"`. Previously
there was effectively one ZeroTier network per clan. Multiple instances where not natively possible.

:::admonition[Do not rename your instances]{type=warning}
Renaming a ZeroTier instance creates a new, disconnected network. Keep the
instance names you already have.

If you want to rename your zerotier instances do so **before** the migration runs.
:::

## Migration Steps

1. **Bump clan-core** in your `flake.nix` and update the lock
   (`nix flake update clan-core`).

2. **Run `clan vars generate`.** Before evaluating any generator, clan runs an
   automatic, value-preserving migration that **moves** your existing ZeroTier
   vars into the new layout. It does not regenerate anything: identities,
   network IDs, and IPs are preserved, and the migration is robust to an
   interrupted prior run. You should see only file moves under `vars/`.

3. **Verify the values did not change.** Confirm each machine kept the same IP
   and network ID, for example:

    ```bash
    clan vars get <machine> zerotier-ip-<machine>-<instance>/ip
    clan vars get <controller> zerotier-network-<instance>/network-id
    ```

4. **Deploy one test machine**, confirm ZeroTier connectivity, then roll
   out to the rest.

## Required config updates if you referenced the old generator

The old `zerotier` generator no longer exists. If your code references `clan.core.vars.generators.zerotier` you need to update it.

### `targetHost`

If you set `clan.core.networking.targetHost`

```nix
clan.core.networking.targetHost =
  "root@[${config.clan.core.vars.generators.zerotier.files.zerotier-ip.value}]";
```

Prefer **removing** the manual setting entirely. This is now handled by the networking module.

If you still want to keep it, rename:

```nix
clan.core.networking.targetHost =
  "root@[${config.clan.core.vars.generators."zerotier-ip-<machine>-<instance>".files.ip.value}]";
```

If you need a NixOS-module that works on any machine:

```nix
{ config, ... }:
let
  # Auto-derived; no need to hardcode the machine name.
  machineName = config.clan.core.settings.machine.name;
  # Your inventory.instances.<name> key (e.g. "net-a"). Not the module name.
  instanceName = "<instance>";
  ztIp = config.clan.core.vars.generators."zerotier-ip-${machineName}-${instanceName}".files.ip.value;
in
{
  environment.etc."zerotier-ip".text = ztIp;
}
```

## Migrate manual peer authorization to `allowedIds`

If you authorized external devices with

`zerotier-members allow <node-id>`

move those node IDs into the controller settings and delete the tool call.

On the controller:

```nix
roles.controller.machines."<controller>".settings.allowedIds = [
  "deadbeef00" # node ID from `zerotier-cli info` on the external device
];
```

- `allowedIds` is preferred. Because the node ID is stable per device.
- `allowedIps` still works if you prefer to authorize by ZeroTier IP, but be aware that the IP depends on the network.

## Problems

In case of any problems reach us on [matrix](https://matrix.to/#/#clan:clan.lol)

## Migrate `clan.core.networking.zerotier.settings`

Assume you previously used custom settings such as `dns`

Migrate:

```diff
-clan.core.networking.zerotier.settings = {
+clan.core.zerotier.networks."<instance>".settings = {
  dns = {
    "domain" = ".app";
    "servers" = [ "$SERVER_IP" ];
  };
  routes = [
    { target = "2000::"; }
  ];
};
```
