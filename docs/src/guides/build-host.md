# Build Host

`deploy.buildHost` tells Clan to run `nix build` on a different machine than the one it is deploying to. The target host stays out of the build entirely: it only receives the finished system closure and activates it. This guide covers when you want that split, how to configure it, and the second SSH hop it introduces.

:::admonition[Do I need this?]{type=note}
Only if the machine you're deploying to is a poor fit for building. Low RAM, slow CPU, flaky network, or no access to a substituter the builder has are all good reasons. If building on the target works fine, leave `buildHost` unset.
:::

## Background

By default, `clan machines update <machine>` evaluates your flake on your workstation, then builds and activates on `deploy.targetHost`. Setting `deploy.buildHost` splits that work. Evaluation still runs locally, but the build runs on a separate host. The finished closure is then copied from the build host to the target over a second SSH connection, and activated there.

Common reasons to split them:

- The target is resource-constrained (a Raspberry Pi, a small VPS).
- The build host has a fast link to a substituter or private cache the target cannot reach.
- You want to keep build load off a production machine.

Private flake inputs are _not_ a reason to set `buildHost`. Clan evaluates your flake on your workstation, so private repositories are fetched locally and never need to be reachable from the build host. See [Private Flake Inputs](/docs/guides/private-inputs) for the full setup.

:::admonition[Architectures Must Match]{type=warning}
`nix build` on the build host compiles natively for its own system. If the target is `aarch64-linux` and the build host is `x86_64-linux`, the build produces the wrong closure. Pick a build host that matches the target's architecture, or arrange cross-compilation yourself.
:::

## 1. Set It in the Inventory

Add `deploy.buildHost` alongside `deploy.targetHost` in `clan.nix`:

```{.nix title="clan.nix"}
inventory.machines.my-machine = {
  deploy.targetHost = "root@target.example.com";
  deploy.buildHost  = "root@builder.example.com";
};
```

The value has the same format as `targetHost`:

```text
user@host:port?SSH_OPTION=SSH_VALUE&SSH_OPTION_2=VALUE_2
```

A few examples:

- `root@builder.example.com`
- `builder.example.com:2222`
- `root@builder.example.com:22?IdentityFile=/path/to/key`

## 2. Or Set It in the Machine Configuration

You can set `buildHost` inside the NixOS configuration of the machine instead. This is useful when the deployment topology belongs with the machine, not the clan-level inventory:

```{.nix title="machines/my-machine/configuration.nix"}
clan.core.networking.buildHost = "root@builder.example.com";
```

Prefer the inventory when you can. It keeps the topology of every machine visible in one place.

## 3. Or Override from the CLI

For one-off deployments, `clan machines update` accepts `--build-host`:

```bash
clan machines update my-machine --build-host root@builder.example.com
```

Pass `localhost` to force a local build, even if the inventory names a remote builder:

```bash
clan machines update my-machine --build-host localhost
```

:::admonition[Resolution Order]{type=note}
Clan resolves `buildHost` in this order, highest priority first:

1. `--build-host` on the command line
2. `inventory.machines.<name>.deploy.buildHost`
3. `clan.core.networking.buildHost` in the machine configuration
4. Default: use `deploy.targetHost` (build on the target itself)
:::

## What Happens During a Deploy

With `buildHost` set, `clan machines update` runs three distinct stages:

1. Your workstation evaluates the flake and uploads the flake source to the build host.
2. The build host runs `nix build` to produce the system closure.
3. The build host runs `nix copy` over SSH to the target host, and Clan activates the new system on the target.

Stage 3 is the one that matters for authentication. The build host opens its own SSH connection to the target, with its own credentials and its own `~/.ssh/known_hosts`. That connection has nothing to do with your workstation's SSH session. It needs:

- A private key on the build host that the target accepts for the user named in `deploy.targetHost`.
- A `known_hosts` entry for the target on the build host.

Neither exists by default.

## Authenticating the Second Hop

The build host has to prove it is allowed to log in to the target. You have two options:

1. Install a dedicated SSH key on the build host and authorize it on the target. This is the path we recommend.
2. Forward your local SSH agent through the build host, so it reuses the keys on your workstation. Quicker to set up, riskier to leave running.

Both options, the tradeoffs, and the step-by-step setup for option 1 are covered in the [SSH Agent Forwarding](/docs/guides/ssh-agent-forwarding) guide. Work through it once per build host, then come back here.

## First Deploy: Host Key Verification

On the first deploy, the target's host key is not yet in the build host's `known_hosts`, and the nested SSH fails with:

```text
Host key verification failed.
error: failed to start SSH connection to '<target-host>'
```

The fix is to pass `--host-key-check accept-new` on the first run. Clan forwards it to the nested SSH that the build host opens, so the target's key is recorded on first use:

```bash
clan machines update my-machine --host-key-check accept-new
```

Subsequent deploys can drop the flag. The mechanism, and a manual alternative using `ssh-keyscan`, are covered in the [Host Key Verification](/docs/guides/ssh-agent-forwarding#host-key-verification) section of the SSH Agent Forwarding guide.

## Using `nixos-rebuild` Directly

If you bypass `clan machines update` and call `nixos-rebuild` by hand, the equivalent flag is `--build-host`:

```bash
nixos-rebuild switch \
  --flake .#my-machine \
  --target-host root@target.example.com \
  --build-host  root@builder.example.com
```

Run `clan vars upload my-machine` first if your configuration uses Clan vars. The full workflow is in [NixOS Rebuild](/docs/guides/nixos-rebuild).

## Troubleshooting

### Permission Denied During Closure Copy

If the deploy fails with `Permission denied (publickey)` while the build host is copying the closure, the build host has no accepted key on the target. Work through the [SSH Agent Forwarding](/docs/guides/ssh-agent-forwarding) guide, which walks through installing a dedicated build-host key.

### Host Key Verification Fails After the Build Succeeds

If the build finishes and the deploy then aborts with `Host key verification failed`, the build host has no `known_hosts` entry for the target. Re-run with `--host-key-check accept-new`, or seed the entry by hand. Both are covered in the [Host Key Verification](/docs/guides/ssh-agent-forwarding#host-key-verification) section.

### The Build Runs on the Target, Not the Builder

The precedence order has silently fallen through to `targetHost`. Check, in order: the `--build-host` flag you passed, the inventory entry in `clan.nix`, and `clan.core.networking.buildHost` in the machine configuration. If none is set, Clan builds on the target by design.

### Architecture Mismatch Between Build Host and Target

If the build aborts with a message along the lines of `a 'x86_64-linux' ... is required to build ..., but I am a 'aarch64-linux'`, the build host and target have different architectures. Pick a build host that matches the target, or build locally with `--build-host localhost`.

## Related

- [SSH Agent Forwarding](/docs/guides/ssh-agent-forwarding) — authenticating the second SSH hop.
- [Private Flake Inputs](/docs/guides/private-inputs) — using private Git repositories as flake inputs without shipping credentials to the builder.
- [NixOS Rebuild](/docs/guides/nixos-rebuild) — using `nixos-rebuild` directly instead of `clan machines update`.
