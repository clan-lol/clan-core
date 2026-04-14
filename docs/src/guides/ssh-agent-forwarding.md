# SSH Agent Forwarding

When you deploy through a separate `buildHost`, Clan opens a second SSH connection from the build host to the target host to activate the new configuration. This guide walks through the recommended way to authenticate that hop: install a dedicated SSH key on the build host. It also covers the shortcut (forwarding your local agent) and why you probably shouldn't use it.

:::admonition[Do I need this?]{type=note}
Only if you set `deploy.buildHost` to something other than `deploy.targetHost`. If they're the same, or `buildHost` is unset, you can skip this guide. If you're new to `buildHost` itself, start with the [Build Host](/docs/guides/build-host) guide and come back here when it points you to this page.
:::

## Background

Setting `deploy.buildHost` tells Clan to run `nixos-rebuild` on that host and then connect from there to the target to switch the configuration. That second connection needs credentials. You have two options:

1. Install a dedicated SSH key on the build host and add its public half to the target host's `authorized_keys`.
2. Forward your local SSH agent through the build host so it can reuse the keys already loaded on your workstation.

Option 1 is the recommended path and the rest of this guide walks through it. Option 2 is covered further down as an alternative.

:::admonition[Private Flake Inputs]{type=tip}
Private Git flake inputs do not require agent forwarding. Clan evaluates your flake on your workstation, so private inputs are fetched locally with your own SSH key and never need to reach the build or target host. See [Private Flake Inputs](/docs/guides/private-inputs) for the full setup.
:::

## Security Considerations

:::admonition[Warning]{type=danger}
Forwarding your SSH agent places your private keys within reach of anyone with root on the build host for the lifetime of the connection. Root on the build host can then authenticate as you to every system listed in your `authorized_keys`. Treat a forwarded agent as a credential you have handed out, not one you still control.
:::

## 1. Declare a Build-Host Key Generator

Open the configuration for your build host and add a `clan vars` generator for an ed25519 key pair. The private half is encrypted at rest and never touches your workstation.

```{.nix title="machines/<build-host>/configuration.nix"}
{ config, ... }:
{
  clan.core.vars.generators.build-host-key = {
    files.private-key = { };
    files.public-key = {
      secret = false;
    };
    script = ''
      ssh-keygen -t ed25519 -f "$out/private-key" -N "" -C "buildhost@${config.clan.core.settings.machine.name}"
      mv "$out/private-key.pub" "$out/public-key"
    '';
  };

  programs.ssh.extraConfig = ''
    Host *
      IdentityFile ${config.clan.core.vars.generators.build-host-key.files.private-key.path}
  '';
}
```

The generator creates the key. The `programs.ssh.extraConfig` block tells SSH on the build host to use it when connecting outward.

## 2. Generate the Key

```bash
clan vars generate <build-host>
```

This runs the generator you just declared and stores the encrypted private key under your clan's `vars/` directory. Run it once per build host.

## 3. Authorize the Key on the Target Host

Instead of copying the public key by hand, read it directly from the build host's generator output. Clan stores public values at a predictable path under the clan directory, so the target host can pull them in at evaluation time.

```{.nix title="machines/<target-host>/configuration.nix"}
{ config, ... }:
let
  buildHostKey = builtins.readFile (
    config.clan.core.settings.directory
    + "/vars/per-machine/<build-host>/build-host-key/public-key/value"
  );
in
{
  users.users.root.openssh.authorizedKeys.keys = [
    buildHostKey
  ];
}
```

Replace `<build-host>` with the name of the machine that runs the build. If Clan deploys as a non-root user on the target, add the key under that user instead.

:::admonition[Evaluation Order]{type=note}
The public key file must exist on disk before the target host is evaluated. Run `clan vars generate <build-host>` (step 2) before you deploy the target.
:::

## 4. Deploy

On the first deploy, the build host has no record of the target's host key yet. Pass `--host-key-check accept-new` so the build host accepts and records the key on first use:

```bash
clan machines update <machine> --host-key-check accept-new
```

Subsequent deploys can drop the flag:

```bash
clan machines update <machine>
```

The build host now authenticates to the target on its own. No agent forwarding required. If the deploy still fails at this step, see [Host Key Verification](#host-key-verification) for the full mechanism and [Troubleshooting](#troubleshooting) for common errors.

---

## Alternative: Enable Agent Forwarding

If you'd rather forward your local agent than manage a build-host key, enable it globally:

```{.nix title="clan.nix"}
clan.core.networking.forwardAgent = true;
```

Or per machine in the inventory:

```{.nix title="clan.nix"}
inventory.machines.my-machine = {
  deploy.targetHost = "root@target.example.com";
  deploy.buildHost  = "root@builder.example.com";
  deploy.forwardAgent = true;
};
```

:::admonition[Resolution Order]{type=note}
Clan resolves `forwardAgent` in this order, highest priority first:

1. `inventory.machines.<name>.deploy.forwardAgent`
2. `clan.core.networking.forwardAgent`
3. Default: `false`
:::

## Host Key Verification

Step 4 passes `--host-key-check accept-new` for a reason. When `deploy.buildHost` is set, `nix copy` runs on the build host and opens its own SSH connection to the target. That connection is verified against the build host's `~/.ssh/known_hosts`, which is a separate file from your workstation's. Without the flag, the nested SSH fails on the first deploy with:

```text
Host key verification failed.
error: failed to start SSH connection to '<target-host>'
```

### Why `--host-key-check` Reaches the Second Hop

Clan forwards the `--host-key-check` setting to the build host and applies it to the SSH connection that the builder opens to the target. A flag you set on your workstation ends up governing a connection two hops away, which is why the fix works without you ever logging in to the build host.

:::admonition[Multiple Build Hosts]{type=note}
If you have more than one build host, each one needs its own `known_hosts` entry for the target. Clan does not sync them. Run the first deploy through each build host with `--host-key-check accept-new`, once per builder. From then on, strict checking takes over on that builder.
:::

## Troubleshooting

### Permission Denied During Deployment

If deployment fails with `Permission denied (publickey)` on the hop from the build host to the target, the build host has no accepted key on the target. Work through steps 1 to 3 above, or enable `forwardAgent` while you investigate.

If you see this error without a separate `buildHost`, agent forwarding will not help. The failure is between your workstation and the target host. Verify that your local user can open a plain SSH session:

```bash
ssh root@<target-host>
```

:::admonition[Automatic Detection]{type=tip}
Clan detects SSH authentication and host-key failures during deployment and prints guidance that points to this page.
:::

## Related

- [Build Host](/docs/guides/build-host) — when and how to set `deploy.buildHost` in the first place.
- [Private Flake Inputs](/docs/guides/private-inputs) — using private Git repositories as flake inputs without agent forwarding.
- [NixOS Rebuild](/docs/guides/nixos-rebuild) — using `nixos-rebuild` directly instead of `clan machines update`.

## References

- [NixOS Manual: SSH Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-openssh)
- [Matrix post-mortem on SSH agent forwarding](https://matrix.org/blog/2019/05/08/post-mortem-and-remediations-for-apr-11-security-incident/#ssh-agent-forwarding-should-be-disabled)
- [GitHub: Deploy Keys](https://docs.github.com/en/developers/overview/managing-deploy-keys)
