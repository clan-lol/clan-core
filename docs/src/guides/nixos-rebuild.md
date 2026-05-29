# NixOS Rebuild

## Can I still use `nixos-rebuild`?

**Yes, you can still use `nixos-rebuild` with Clan!**

Clan is built on top of standard `NixOS` and uses `nixos-rebuild` internally.
However, there are important considerations when using `nixos-rebuild` directly instead of `clan machines update`.

### Important Considerations

:::admonition[Vars Must Be Uploaded First]{type=warning}
If your configuration uses Clan vars, failing to run `clan vars upload` before `nixos-rebuild` will result in missing secrets and potentially broken services.
:::

:::admonition[Build Host Configuration]{type=info}
Clan automatically handles build host configuration based on your machine settings.
When using `nixos-rebuild` manually, you need to specify `--build-host` and `--target-host` options yourself.
:::

### How Clan Uses nixos-rebuild

Clan doesn't replace `nixos-rebuild` - it enhances it. When you run `clan machines update`, Clan:

1. Generates and uploads secrets/variables (if any)
2. Uploads the flake source to the target/build host (if needed)
3. Builds the NixOS system closure
4. Sets the system profile (`nix-env --set`)
5. Runs `switch-to-configuration boot` to register the new generation in the bootloader
6. Runs `switch-to-configuration switch` to live-activate the new configuration
7. If the live switch is blocked by switch inhibitors (critical component changes
   like dbus or systemd), reports the failure and suggests rebooting — the new
   configuration is already registered for the next boot

You can pass `--no-check` (or set `NIXOS_NO_CHECK=1`) to force past switch
inhibitors when you know the live switch is safe.

### When You Need `clan vars upload`

If your Clan configuration uses **variables (vars)** - generated secrets, keys, or configuration values - you **must** run `clan vars upload` before using `nixos-rebuild` directly.

#### Systems that use vars include:

- Any `clanServices` with generated secrets (zerotier, borgbackup, etc.)
- Custom generators that create passwords or keys
- Services that need shared configuration values

#### Systems that don't need vars:

- Basic NixOS configurations without clan-specific services
- Static configurations with hardcoded values
- Systems using only traditional NixOS secrets management

### Manual nixos-rebuild Workflow

When you want to use `nixos-rebuild` directly:

#### Step 1: Upload vars (if needed)

```bash
# Upload secret vars to the target device
clan vars upload my-machine
```

#### Step 2: Run nixos-rebuild

```bash
nixos-rebuild switch --flake .#my-machine --target-host root@target-ip --build-host local
```

### Related Documentation

- [Getting-started](/docs/getting-started/quick-start)
- [Vars](/docs/guides/vars/intro-to-vars)
