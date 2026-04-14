# Private Flake Inputs

This guide walks through pulling a private Git repository into your flake inputs, using a Gitea, GitHub, or GitLab repository as the example. The payoff: `clan machines update` deploys the private code without you installing credentials on the build host or the target host, and without forwarding your SSH agent.

:::admonition[Prerequisites]{type=note}
An SSH key on your workstation (see [Create an SSH key](/docs/getting-started/create-an-ssh-key)) and an account on the Git host that can read the private repository.
:::

## Background

When you run `clan machines update`, Clan evaluates your flake on your workstation before any build or deploy happens. Evaluation is what fetches flake inputs, so the fetch runs under your local user, with your local SSH keys, against whatever host the input URL points at. Once evaluation is done, Clan ships the resolved source to the build host. The build host and target host never see the private URL and never need credentials for it.

The practical consequence: if your workstation can `git clone` the private repository, your Clan deploys can use it as a flake input.

## 1. Register Your SSH Key on the Git Host

Upload your workstation's public key to the Git host that serves the private repository:

- **Gitea:** Profile → Settings → SSH / GPG Keys → Add Key.
- **GitHub:** Settings → SSH and GPG keys → New SSH key.
- **GitLab:** Preferences → SSH Keys → Add new key.

Paste the contents of `~/.ssh/id_ed25519.pub`, or whichever public key you plan to use.

Then verify from the workstation that the key works:

```bash
ssh -T gitea@gitea.example.com
```

A response from the Git host confirms the key is registered. A direct `git clone` of one of your private repositories is an equally good check.

## 2. Declare the Input with an SSH URL

In your `flake.nix`, add the input using the `ssh://` URL for the repository:

```{.nix title="flake.nix"}
{
  inputs = {
    clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";

    my-private-pkgs = {
      type = "git";
      url  = "ssh://gitea@gitea.example.com/Luis/my-private-nix-packages.git";
    };
  };

  # ... outputs
}
```

The exact URL depends on your Git host:

- **Gitea:** `ssh://gitea@<host>/<user>/<repo>.git`
- **GitHub:** `ssh://git@github.com/<user>/<repo>.git`
- **GitLab:** `ssh://git@gitlab.com/<group>/<repo>.git`

:::admonition[Use `type = "git"`, Not the Shorthand]{type=tip}
The shorthand fetchers `github:owner/repo` and `gitlab:owner/repo` go over HTTPS and do not use your SSH key. For private repositories, use an explicit `type = "git"` input with an `ssh://` URL. Nix will hand the transport to `git`, which then picks up your SSH configuration and agent.
:::

## 3. Lock the Input

```bash
nix flake lock
```

Running `nix flake lock` populates `flake.lock` with the current revision of the new input. The locked revision is a Git hash and a `narHash`, not a secret, so `flake.lock` is safe to commit. Nix will not reach out to the private repository again until you explicitly refresh the lock:

```bash
nix flake update my-private-pkgs
```

## 4. Use It in a Machine Configuration

Consume the input like any other flake input:

```{.nix title="machines/my-machine/configuration.nix"}
{ pkgs, inputs, ... }:
{
  environment.systemPackages = [
    inputs.my-private-pkgs.packages.${pkgs.system}.my-tool
  ];
}
```

## 5. Deploy

```bash
clan machines update my-machine
```

Clan evaluates the flake on your workstation. Nix calls out to `git`, which uses your local SSH key to authenticate against the Git host and fetch the revision pinned in `flake.lock`. The resolved sources, including the private repository, are archived and uploaded to the build host. The build host never speaks to the private Git host and never sees your SSH key.

If you also set `deploy.buildHost`, the build-to-target SSH hop is a separate authentication problem from flake input fetching. See the [Build Host](/docs/guides/build-host) guide for that one.

## Troubleshooting

### Permission Denied When Running `nix flake lock`

If `nix flake lock` aborts with `Permission denied (publickey)`, your workstation cannot authenticate to the Git host. Re-run the verification from section 1:

```bash
ssh -T gitea@gitea.example.com
```

If that fails, fix the SSH key registration on the Git host before touching the flake.

### `git` Fails with Exit Code 128

Usually either an authentication or a URL problem. Confirm the URL by cloning the repository directly:

```bash
git clone ssh://gitea@gitea.example.com/Luis/my-private-nix-packages.git
```

If `git clone` works but `nix flake lock` still fails, check that you used `type = "git"` in the input. The `github:` and `gitlab:` shorthands go over HTTPS and ignore your SSH configuration.

### The Build Host Tries to Fetch the Private Repository

It shouldn't. Clan evaluates the flake on your workstation, so by the time the build host receives the sources, the private repository has already been resolved. If the build host really is reaching out to the Git host, you are probably running `nixos-rebuild` directly with `--flake` pointing at a URL the build host has to resolve on its own. Either switch to `clan machines update`, or follow the [NixOS Rebuild](/docs/guides/nixos-rebuild) guide to upload the flake source yourself first.

## Related

- [Build Host](/docs/guides/build-host) — when deploys run through a separate builder, and how the second SSH hop is authenticated.
- [SSH Agent Forwarding](/docs/guides/ssh-agent-forwarding) — why agent forwarding is not required for private inputs.
- [NixOS Rebuild](/docs/guides/nixos-rebuild) — using `nixos-rebuild` directly instead of `clan machines update`.
