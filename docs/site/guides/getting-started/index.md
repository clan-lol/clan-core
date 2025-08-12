# :material-clock-fast: Getting Started

Ready to create your own Clan and manage a fleet of machines? Follow these simple steps to get started.

This guide walks your through setting up your own declarative infrastructure using clan, git and flakes. By the end of this, you will have one or more machines integrated and installed. You can then import your existing NixOS configuration into this setup if you wish.

The following steps are meant to be executed on the machine on which to administer the infrastructure.

In order to get started you should have at least one machine with either physical or ssh access available as an installation target. Your local machine can also be used as an installation target if it is already running NixOS.

## Prerequisites

=== "**Linux**"

    Clan requires Nix to be installed on your system. Run the following command to install Nix:

    ```shellSession
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

    ```shellSession
    curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
    ```

    If you have previously installed Nix, make sure `experimental-features = nix-command flakes` is present in `~/.config/nix/nix.conf` or `/etc/nix/nix.conf`. If this is not the case, please add it to `~/.config/nix/nix.conf`.

## Create a new clan

Initialize a new clan flake

```shellSession
nix run https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli --refresh -- flakes create
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
For example, you might see something like:

```{ .console .no-copy }
$ cd my-clan
$ ls
clan.nix  flake.lock  flake.nix  modules  sops
```



Don’t worry if your output looks different — Clan templates evolve over time.

To interact with your newly created clan the you need to load the `clan` cli-package it into your environment by running:

=== "Automatic (direnv, recommended)"
    - prerequisite: [install nix-direnv](https://github.com/nix-community/nix-direnv)

    ```shellSession
    direnv allow
    ```

=== "Manual (nix develop)"

    ```shellSession
    nix develop
    ```

verify that you can run `clan` commands:

```shellSession
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

