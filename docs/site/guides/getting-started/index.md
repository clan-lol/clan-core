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

Add the Clan CLI into your environment:

```bash
nix shell git+https://git.clan.lol/clan/clan-core#clan-cli --refresh
```

```terminalSession
clan --help
```

Should print the avilable commands.

Also checkout the [cli-reference documentation](../../reference/cli/index.md).

## Initialize Your Project

If you want to migrate an existing project, follow this [guide](../migrations/migration-guide.md).

Set the foundation of your Clan project by initializing it by running:

```bash
clan flakes create my-clan
```

This command creates a `flake.nix` and some other files for your project.

## Explore the Project Structure

Take a lookg at all project files:

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

Don’t worry if your output looks different—the template evolves over time.

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

```
clan machines list
```

If you see no output yet, that’s expected — [add machines](./add-machines.md) to populate it.

---

## Next Steps

You can continue with **any** of the following steps at your own pace:

- [x] [Install Nix & Clan CLI](./index.md)
- [x] [Initialize Clan](./index.md#initialize-your-project)
- [ ] [Create USB Installer (optional)](./installer.md)
- [ ] [Add Machines](./add-machines.md)
- [ ] [Add Services](./add-services.md)
- [ ] [Configure Secrets](./secrets.md)
- [ ] [Deploy](./deploy.md) - Requires configured secrets
- [ ] [Setup CI (optional)](./check.md)
