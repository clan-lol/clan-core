# SSH Agent Forwarding

## Overview

SSH agent forwarding allows your local SSH keys to be temporarily available on remote hosts during deployment. While convenient for accessing private repositories during builds, it has security implications that you should understand before enabling it.

## Security Considerations

**⚠️ Warning:** SSH agent forwarding can be a security risk!

When agent forwarding is enabled:

- Your SSH keys are temporarily available on the remote host
- Any user with root access on the remote host could potentially use your forwarded keys
- The keys remain accessible for the duration of your SSH connection

**Best Practice:** Only enable agent forwarding for machines you fully trust, and consider more secure alternatives when possible.

## Configuration

### Default Behavior

Starting from [PR #5803](https://git.clan.lol/clan/clan-core/pulls/5803), SSH agent forwarding is **disabled by default** for security reasons.

### Global Configuration

To enable SSH agent forwarding for all machines:

```nix
{
  clan.core.networking.forwardAgent = true;
}
```

Add this to your NixOS configuration or flake.

### Per-Machine Configuration

To enable or disable agent forwarding for specific machines in your inventory:

```nix
{
  inventory.machines = {
    builder-machine = {
      deploy.targetHost = "builder.example.com";
      deploy.forwardAgent = true; # Enable for this machine only
    };

    web-server = {
      deploy.targetHost = "web.example.com";
      # Inherits global setting or defaults to false
    };

    sensitive-machine = {
      deploy.targetHost = "sensitive.example.com";
      deploy.forwardAgent = false; # Explicitly disable even if global is true
    };
  };
}
```

### Configuration Priority

The configuration is resolved in this order:

1. Per-machine `inventory.machines.<name>.deploy.forwardAgent` (highest priority)
2. Global `clan.core.networking.forwardAgent`
3. Secure default: `false` (if nothing is configured)

## Use Cases

### When You Might Need Agent Forwarding

- Your flake has private Git repository inputs using SSH URLs (e.g., `git@github.com:org/private-repo.git`)
- The build/target host doesn't have its own SSH keys configured for accessing private repositories
- Quick prototyping or development environments

### When to Avoid Agent Forwarding

- Production deployments
- Machines you don't fully trust
- Shared or multi-user systems
- When more secure alternatives are available

## Secure Alternatives

Instead of using SSH agent forwarding, consider these more secure approaches:

### 1. Deploy Keys (Recommended)

Use clan vars to automatically generate and securely manage deploy keys:

#### Step 1: Configure the machine to generate a deploy key

```nix
{
  clan.core.vars.generators.deploy-key = {
    files.private-key = { };
    files.public-key = { };
    script = ''
      ssh-keygen -t ed25519 -f "$out/private-key" -N "" -C "deploy-key@''${machine_name}"
      mv "$out/private-key.pub" "$out/public-key"
    '';
  };

  # Configure SSH to use the deploy key
  programs.ssh.extraConfig = ''
    Host github.com
      IdentityFile ${config.clan.core.vars.generators.deploy-key.files.private-key.path}
      StrictHostKeyChecking accept-new
  '';
}
```

#### Step 2: Generate the deploy key

```bash
clan vars generate <machine-name> deploy-key
```

#### Step 3: Retrieve and add the public key to your Git repository

```bash
# Get the public key
clan vars get <machine-name> deploy-key.public-key

# Add this as a deploy key in your repository settings:
# - GitHub: Settings → Deploy keys → Add deploy key
# - GitLab: Settings → Repository → Deploy keys
```

**Benefits of this approach:**

- Automatic key generation via clan vars
- Secure secret management - keys never touch your local filesystem
- Different deploy keys per machine
- Keys are encrypted at rest
- No manual key generation or cleanup needed

### 2. HTTPS with Access Tokens

Use HTTPS URLs with access tokens instead of SSH. Configure tokens via netrc or nix access-tokens settings.

See the [Nix manual](https://nixos.org/manual/nix/stable/command-ref/conf-file.html#conf-access-tokens) for details on configuring access tokens.

## Troubleshooting

### Error: "Permission denied (publickey)"

If you see this error during deployment and have private flake inputs:

1. **Quick fix** (if you trust the host): Enable agent forwarding as shown above
2. **Recommended**: Use one of the secure alternatives listed above

### Error Detection

Clan will automatically detect SSH authentication failures during deployment and provide guidance:

```text
SSH authentication failed during deployment. This may be caused by
private Git repositories in your flake inputs.

To fix this, you have several options:

1. Enable SSH agent forwarding (quick fix, but has security implications):
   - Per-machine: Set `inventory.machines.machine-name.deploy.forwardAgent = true;`
   - Globally: Set `clan.core.networking.forwardAgent = true;` in your configuration

2. Use more secure alternatives:
   - Install deploy keys directly on the build/target host
   - Use HTTPS URLs with access tokens instead of SSH URLs
   - Configure SSH keys on the remote host that has access to private repositories
```

## Migration Guide

If you're upgrading from an older version where agent forwarding was enabled by default:

### Step 1: Identify Machines That Need Forwarding

Check which machines have private flake inputs:

```bash
# Review your flake inputs
nix flake metadata
```

### Step 2: Choose Your Approach

- **Option A:** Enable globally if all machines are trusted:

    ```nix
  clan.core.networking.forwardAgent = true;
    ```

- **Option B:** Enable per-machine for specific needs:

    ```nix
  inventory.machines.<name>.deploy.forwardAgent = true;
    ```

- **Option C (Recommended):** Migrate to secure alternatives (deploy keys, HTTPS tokens, etc.)

### Step 3: Test Your Deployments

After configuration, test your deployments to ensure everything works:

```bash
clan machines update <machine-name>
```

## References

- [NixOS Manual: SSH Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-openssh)
- [SSH Agent Forwarding Security](https://matrix.org/blog/2019/05/08/post-mortem-and-remediations-for-apr-11-security-incident/#ssh-agent-forwarding-should-be-disabled)
- [GitHub: Deploy Keys](https://docs.github.com/en/developers/overview/managing-deploy-keys)
