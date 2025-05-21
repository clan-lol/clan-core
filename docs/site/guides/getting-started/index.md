# :material-clock-fast: Getting Started

Ready to create your own Clan and manage a fleet of machines? Follow these simple steps to get started.

By the end of this guide, you'll have a fresh NixOS configuration ready to push to one or more machines. You'll create a new Git repository and a flake, and all you need is at least one machine to push to. This is the easiest way to begin, and we recommend you to copy your existing configuration into this new setup!


### Prerequisites

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

### Step 1: Add Clan CLI to Your Shell

Add the Clan CLI into your development workflow:

```bash
nix shell git+https://git.clan.lol/clan/clan-core#clan-cli --refresh
```

You can find reference documentation for the `clan` CLI program [here](../../reference/cli/index.md).

Alternatively you can check out the help pages directly:
```terminalSession
clan --help
```

### Step 2: Initialize Your Project

If you want to migrate an existing project, follow this [guide](../migrations/migration-guide.md).

Set the foundation of your Clan project by initializing it by running:

```bash
clan flakes create my-clan
```

This command creates the `flake.nix` and `.clan-flake` files for your project.
It will also generate files from a default template, to help show general clan usage patterns.

### Step 3: Verify the Project Structure

Ensure that all project files exist by running:

```bash
cd my-clan
tree
```

This should yield the following:

``` { .console .no-copy }
.
├── flake.nix
├── machines
│   ├── jon
│   │   ├── configuration.nix
│   │   └── hardware-configuration.nix
│   └── sara
│       ├── configuration.nix
│       └── hardware-configuration.nix
└── modules
    └── shared.nix

5 directories, 9 files
```

??? info "Recommended way of sourcing the `clan` CLI tool"

    The default template adds the `clan` CLI tool to the development shell.
    This means that you can access the `clan` CLI tool directly from the folder
    you are in right now.

    In the `my-clan` directory, run the following command:

    ```
    nix develop
    ```

    This will ensure the `clan` CLI tool is available in your shell environment.

    To automatically add the `clan` CLI tool to your environment without having to
    run `nix develop` every time, we recommend setting up [direnv](https://direnv.net/).


```bash
clan machines list
```

``` { .console .no-copy }
jon
sara
```

!!! success

    You just successfully bootstrapped your first Clan.

