# Install Nix and direnv

Clan is built on [Nix](https://nixos.org/). The `clan` CLI, every template, and every machine configuration are fetched and evaluated through Nix, so you need it installed on any machine you want to use as a setup machine. [direnv](https://direnv.net/) is optional for everyday Clan use but required when you work on Clan itself, because it loads the right devshell as soon as you `cd` into the repository.

If you already run NixOS, you can skip the Nix section. Everything else applies equally.

## Install Nix

Install Nix through the official installer:

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://artifacts.nixos.org/nix-installer | sh -s -- install --enable-flakes
```

This fetches the [NixOS installer](https://github.com/NixOS/nix-installer/releases) and runs it. The script sets up `/nix`, configures the daemon, and turns on the `nix-command` and `flakes` experimental features that Clan relies on. Passing `--enable-flakes` skips the interactive prompt the installer would otherwise show.

Once the installer finishes, open a new shell and confirm the install:

```bash
nix --version
```

You should see a version string. If the command is not found, restart your terminal so the updated `PATH` takes effect.

:::admonition[Already on NixOS?]{type=tip}
NixOS ships with Nix, so you can skip this section. Make sure `experimental-features = nix-command flakes` is present in your `nix.conf` or `nix.settings.experimental-features` in your NixOS configuration.
:::

## Install direnv

direnv watches for an `.envrc` file in the current directory and loads its environment automatically. In Clan, every devshell is wired up through an `.envrc`, so direnv makes the right tools appear the moment you enter a directory and disappear when you leave.

Install `direnv` and its Nix integration through Nix itself:

```bash
nix profile add nixpkgs#nix-direnv nixpkgs#direnv
```

`nix-direnv` is the shim that makes direnv cache Nix devshells, so they only rebuild when inputs change.

Next, [hook direnv into your shell](https://direnv.net/docs/hook.html). For bash and zsh in one go:

```bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc && echo 'eval "$(direnv hook bash)"' >> ~/.bashrc && eval "$SHELL"
```

The `eval "$SHELL"` at the end restarts your shell so the hook is active immediately.

From now on, every time you `cd` into a directory that contains an `.envrc`, direnv will ask you to approve it once:

```bash
direnv: error .envrc is blocked. Run `direnv allow` to approve its content
```

Run `direnv allow` in that directory and the environment loads. This only needs to happen once per `.envrc`, and again whenever the file changes.

## Next steps

With Nix installed you are ready to follow the [Quick Start](/docs/getting-started/quick-start) or any of the full install guides. If you intend to contribute to Clan itself, continue with the [Contributing guide](/docs/guides/contributing/CONTRIBUTING), which relies on direnv to load the development environment.
