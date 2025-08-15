# :material-clock-fast: Getting Started

Ready to manage your fleet of machines? 

We will create a declarative infrastructure using **clan**, **git**, and **nix flakes**.

You'll finish with a centrally managed fleet, ready to import your existing NixOS configuration.

## Prerequisites

Make sure you have the following:

* 💻 **Administration Machine**: Run the setup commands from this machine.
* 🛠️ **Nix**: The Nix package manager, installed on your administration machine.

    ??? info "**How to install Nix (Linux / MacOS / NixOS)**"

        **On Linux or macOS:**

        1.  Run the recommended installer:
            ```shellSession
            curl --proto '=https' --tlsv1.2 -sSf -L [https://install.determinate.systems/nix](https://install.determinate.systems/nix) | sh -s -- install
            ```

        2.  After installation, ensure flakes are enabled by adding this line to `~/.config/nix/nix.conf`:
            ```
            experimental-features = nix-command flakes
            ```

        **On NixOS:**

        Nix is already installed. You only need to enable flakes for your user in your `configuration.nix`:

        ```nix
        {
          nix.settings.experimental-features = [ "nix-command" "flakes" ];
        }
        ```
        Then, run `nixos-rebuild switch` to apply the changes.

* 🎯 **Target Machine(s)**: A remote machine with SSH, or your local machine (if NixOS).

## Create a New Clan

1. Navigate to your desired directory:
    
    ```shellSession
    cd <your-directory>
    ```

2. Create a new clan flake:

    **Note:** This creates a new directory in your current location

    ```shellSession
    nix run https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli --refresh -- flakes create
    ```

3. Enter a **name** in the prompt:

    ```terminalSession
    Enter a name for the new clan: my-clan
    ```

## Project Structure

Your new directory, `my-clan`, should contain the following structure:

```
my-clan/
├── clan.nix
├── flake.lock
├── flake.nix
├── modules/
└── sops/
```

!!! note "Templates"
    This is the structure for the `default` template. 

    Use `clan templates list` and `clan templates --help` for available templates & more. Keep in mind that the exact files may change as templates evolve.


## Activate the Environment

To get started, `cd` into your new project directory.

```shellSession
cd my-clan
```

Now, activate the environment using one of the following methods.

=== "Automatic (direnv, recommended)"
    **Prerequisite**: You must have [nix-direnv](https://github.com/nix-community/nix-direnv) installed.

    Run `direnv allow` to automatically load the environment whenever you enter this directory.
    ```shellSession
    direnv allow
    ```

=== "Manual (nix develop)"
    Run nix develop to load the environment for your current shell session.

    ```shellSession
    nix develop
    ```

## Verify the Setup

Once your environment is active, verify that the clan command is available by running:

```shellSession
clan show
```

You should see the default metadata for your new clan:

```shellSession
Name: __CHANGE_ME__
Description: None
```

This confirms your setup is working correctly. 

You can now change the default name by editing the `meta.name` field in your `clan.nix` file.

```{.nix title="clan.nix" hl_lines="3"}
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "__CHANGE_ME__";

  # ...
  # elided
}
```

