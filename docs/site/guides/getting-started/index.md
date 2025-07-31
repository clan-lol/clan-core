# :material-clock-fast: Getting Started

Ready to create your own Clan and manage a fleet of machines? Follow these simple steps to get started.

By the end of this guide, you'll have a fresh NixOS configuration ready to push to one or more machines. You'll create a new Git repository and a flake, and all you need is at least one machine to push to. This is the easiest way to begin, and we recommend you to copy your existing configuration into this new setup!

## Prerequisites

=== "**Linux**"

    Clan requires Nix to be installed on your system. Run the following command to install Nix:

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
    ```

    If you have previously installed Nix, make sure `experimental-features = nix-command flakes` is present in `~/.config/nix/nix.conf` or `/etc/nix/nix.conf`. If this is not the case, please add it to `~/.config/nix/nix.conf`.

=== "**NixOS**"

    If you run NixOS the `nix` binary is already installed.

    You will also need to enable the `nix-command` and `flakes` experimental features in your `configuration.nix`:

    ```nix
    { nix.settings.experimental-features = [ "nix-command" "flakes" ]; }
    ```

=== "**macOS**"

    Clan requires Nix to be installed on your system. Run the following command to install Nix:

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
    ```

    If you have previously installed Nix, make sure `experimental-features = nix-command flakes` is present in `~/.config/nix/nix.conf` or `/etc/nix/nix.conf`. If this is not the case, please add it to `~/.config/nix/nix.conf`.

## Add Clan CLI to Your Shell

Create a new clan

```bash
nix run git+https://git.clan.lol/clan/clan-core#clan-cli --refresh -- flakes create
```

This should prompt for a *name*:

```terminalSession
Enter a name for the new clan: my-clan
```

Enter a *name*, confirm with *enter*. A directory with that name will be created and initialized.

!!! Note
    This command uses the `default` template

    See `clan templates list` and the `--help` reference for how to use other templates.

## Explore the Project Structure

Take a look at all project files:

```bash
cd my-clan
tree
```

For example, you might see something like:

``` { .console .no-copy }
.
├── flake.nix
├── machines/
├── modules/
└── README.md
```

Don’t worry if your output looks different — Clan templates evolve over time.

To interact with your newly created clan the you need to load the `clan` cli-package it into your environment by running:

=== "Automatic (direnv, recommended)"
    - prerequisite: [install nix-direnv](https://github.com/nix-community/nix-direnv)

    ```
    direnv allow
    ```

=== "Manual (nix develop)"

    ```
    nix develop
    ```

verify that you can run `clan` commands:

```bash
clan show
```

You should see something like this:

```shellSession
Name: __CHANGE_ME__
Description: None
```

To change the name of your clan edit `meta.name` in the `clan.nix` or `flake.nix` file

```{.nix title="clan.nix" hl_lines="3"}
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "__CHANGE_ME__";

  # ...
  # elided
}
```

