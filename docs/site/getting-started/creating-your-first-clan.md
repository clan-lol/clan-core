## Summary

Ready to manage your fleet of machines?

In this guide, we will create a declarative infrastructure using **clan**, **git**, and **nix flakes**.

You'll finish with a centrally managed fleet, ready to import your existing NixOS configuration.


## Requirements

Make sure you have the following:

* 💻 **Setup Device**: A Linux machine from which the setup commands will be run.

!!! Warning "Operating System Recommendations"
    We are currently working on more refined operating system recommendations.

    - Minimum system requirements: 2 CPUs, 4GB RAM, 30gb HDD space, network interface

    - We currently recommend NixOS 25.11 for this guide, but other Linux systems are supported, too.

    - Root user access will be required throughout the whole setup.


* 🛠️ **Nix**: The Nix package manager installed on your setup device.

    ??? info "**How to install Nix**"

        **On Linux (or macOS):**

        1.  Run the recommended installer:
            ```shellSession
            curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
            ```

        2.  After installation, ensure flakes are enabled by adding this line to `~/.config/nix/nix.conf`:
            ```
            experimental-features = nix-command flakes
            ```

        **On NixOS:**

        Nix is already installed.
        You only need to enable flakes for your user via `nano /etc/nixos/configuration.nix`:

        ```nix
        {
          nix.settings.experimental-features = [ "nix-command" "flakes" ];
        }
        ```
        Then, run `nixos-rebuild switch` to apply the changes.

*  🛠️ **direnv**: Many commands in this guide will require direnv to be installed on your setup device.

    ??? info "**How to install direnv**"

        === "NixOS (recommended)"
            1. Add the required lines to your `configuration.nix`:

                ```nix
                {
                  programs.direnv.enable = true;
                  programs.direnv.nix-direnv.enable = true;
                }
                ```

            2. Run:

                ```bash
                sudo nixos-rebuild switch
                ```

            3. Verify installation:

                ```bash
                direnv --version
                ```

        === "Other Linux"
            1. Install direnv:

                ```bash
                sudo apt install direnv
                ```
                or for Arch:
                ```bash
                sudo pacman -S direnv
                ```

            2. Add a hook to your shell:

                ```bash
                echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
                ```
                or for zsh:
                ```bash
                echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
                ```

            3. Restart your shell and then allow direnv for the current folder to test if it worked:

                ```bash
                direnv allow
                ```

* 🎯 **Target Device(s)**: Any number of remote Linux or MacOS devices with SSH root access to. If your setup machine is running on nixOS, it can also be included in the Clan we are going to build, but we will not address this option in this guide.

* Expected knowledge levels for this guide:
    Linux 2/5 - nixOS 0/5 - Computer Networks 1/5

* Estimated time for this step: 20 minutes


## Create a New Clan

A "Clan" is the top level concept of the environment you are building.

In your Clan, you will create and manage your machines, users, and services. It can later also define the relation between services and machines via roles.

1. Navigate to your desired directory:

    ```shellSession
    cd <MY-DIRECTORY>
    ```

2. Create a new clan flake:

    **Note:** This creates a new directory in your current location. Depending on your connection speed, this step may take a few minutes.

    ```shellSession
    nix run "https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-cli" --refresh -- flakes create
    ```

3. Enter a **name** in the prompt, for example `MY-NEW-CLAN`:

    ```terminalSession
    Enter a name for the new clan: MY-NEW-CLAN
    ```

## Project Structure

Your new directory, `MY-NEW-CLAN`, should contain the following structure:

```
MY-NEW-CLAN/
├── clan.nix
├── flake.lock
├── flake.nix
├── modules/
└── sops/
```

!!! note "Templates"
    This is the structure for the `default` template.

    Use `clan templates list` and `clan templates --help` for available templates & more. Keep in mind that the exact files may change as templates evolve.


## Activating the Environment

To get started, `cd` into your new project directory.

```shellSession
cd MY-NEW-CLAN
```

Now, activate the environment using one of the following methods.

=== "Automatic (direnv, recommended)"
    If you installed direnv correctly following the required steps before, you should be presented with an error message now:

    `direnv: error /MY-DIRECTORY/MY-NEW-CLAN/.envrc is blocked. Run direnv allow to approve its content`

    To continue, simply allow direnv in your Clan directory:

    ```bash
    direnv allow
    ```

=== "Manual (nix develop)"
    Run nix develop to load the environment manually:

    ```bash
    nix develop
    ```

## Renaming Your Clan

You can now change the default name and tld by editing the `meta.name` and `meta.domain` fields in your `clan.nix` file.

The meta.name will reflect the name of your clan. It is recommended to use the same name you entered during the creation process.

The metal.domain will function as your internal top level domain. Select something catchy, like clan.lol

Feel obliged to change the following lines

```{.nix title="clan.nix" hl_lines="3 4 5"}
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "fancyclan";
  meta.domain = "fancydomain";
  meta.description = "My selfhosted homelab";

  # ...
  # elided
}
```

## Checkpoint

Once your [environment is active](#activating-the-environment), verify that the clan command is available by running:

```shellSession
clan show
```

You should see the default metadata for your new clan:

```shellSession
Name: __CHANGE_ME__
Description: None
```

This confirms your setup is working correctly.

## Up Next

We will add machines to your freshly created clan during the next step.
