# Can I still use `nixos-rebuild`?

**Yes, you can still use `nixos-rebuild` with clan!**

Clan is built on top of standard `NixOS` and uses `nixos-rebuild` internally.
However, there are important considerations when using `nixos-rebuild` directly instead of `clan machines update`.

## Important Considerations

!!! warning "Vars Must Be Uploaded First"
    If your configuration uses clan vars, failing to run `clan vars upload` before `nixos-rebuild` will result in missing secrets and potentially broken services.

!!! info "Build Host Configuration"
    Clan automatically handles build host configuration based on your machine settings.
    When using `nixos-rebuild` manually, you need to specify `--build-host` and `--target-host` options yourself.

## How Clan Uses nixos-rebuild

Clan doesn't replace `nixos-rebuild` - it enhances it. When you run `clan machines update`, clan:

1. Generates and uploads secrets/variables (if any)
2. Uploads the flake source to the target/build host (if needed)
3. Runs `nixos-rebuild switch` with the appropriate options
4. Handles remote building and deployment automatically

Under the hood, clan executes commands like:

```bash
nixos-rebuild switch --fast --build-host builtHost --flake /path/to/flake#machine-name
```

## When You Need `clan vars upload`

If your clan configuration uses **variables (vars)** - generated secrets, keys, or configuration values - you **must** run `clan vars upload` before using `nixos-rebuild` directly.

### Systems that use vars include:

- Any `clanModules` with generated secrets (zerotier, borgbackup, etc.)
- Custom generators that create passwords or keys
- Services that need shared configuration values

### Systems that don't need vars:

- Basic NixOS configurations without clan-specific services
- Static configurations with hardcoded values
- Systems using only traditional NixOS secrets management

## Manual nixos-rebuild Workflow

When you want to use `nixos-rebuild` directly:

### Step 1: Upload vars (if needed)

```bash
# Upload secret vars to the target machine
clan vars upload my-machine
```

### Step 2: Run nixos-rebuild

```bash
nixos-rebuild switch --flake .#my-machine --target-host root@target-ip --build-host local
```

## Related Documentation

- [Update Your Machines](getting-started/update.md) - Using clan's update command
- [Variables (Vars)](vars/vars-overview.md) - Understanding the vars system
