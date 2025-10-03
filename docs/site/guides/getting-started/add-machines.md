Machines can be added using the following methods

- Create a file `machines/{machine_name}/configuration.nix` (See: [File Autoincludes](../inventory/autoincludes.md))
- Imperative via cli command: `clan machines create`
- Editing nix expressions in flake.nix See [`clan-core.lib.clan`](/options/?scope=Flake Options (clan.nix file))

See the complete [list](../inventory/autoincludes.md) of auto-loaded files.

## Create a machine

=== "clan.nix (declarative)"

    ```{.nix hl_lines="3-4"}
    {
        inventory.machines = {
            # Define a machine
            jon = { };
        };

        # Additional NixOS configuration can be added here.
        # machines/jon/configuration.nix will be automatically imported.
        # See: https://docs.clan.lol/guides/more-machines/#automatic-registration
        machines = {
            # jon = { config, ... }: {
            #   environment.systemPackages = [ pkgs.asciinema ];
            # };
        };
    }
    ```

=== "CLI (imperative)"

    ```sh
    clan machines create jon
    ```

    The imperative command might create a machine folder in `machines/jon`
    And might persist information in `inventory.json`

### Configuring a machine

!!! Note
    The option: `inventory.machines.<name>` is used to define metadata about the machine
    That includes for example `deploy.targethost` `machineClass` or `tags`

    The option: `machines.<name>` is used to add extra *nixosConfiguration* to a machine

Add the following to your `clan.nix` file for each machine.
This example demonstrates what is needed based on a machine called `jon`:

```{.nix .annotate title="clan.nix" hl_lines="3-6 15-19"}
{
    inventory.machines = {
        jon = {
            # Define tags here (optional)
            tags = [ ]; # (1)
        };
        sara = {
            deploy.targetHost = "root@sara";
            tags = [ ];
        };
    };
    # Define additional nixosConfiguration here
    # Or in /machines/jon/configuration.nix (autoloaded)
    machines = {
        jon = { config, pkgs, ... }: {
            users.users.root.openssh.authorizedKeys.keys = [
                "ssh-ed25519 AAAAC3NzaC..." # elided (2)
            ];
        };
    };
}
```

1. Tags can be used to automatically add this machine to services later on. - You dont need to set this now.
2. Add your *ssh key* here - That will ensure you can always login to your machine via *ssh* in case something goes wrong.

### (Optional) Create a `configuration.nix`

```nix title="./machines/jon/configuration.nix"
{
    imports = [
        # enables GNOME desktop (optional)
        ../../modules/gnome.nix
    ];

    # Set nixosOptions here
    # Or import your own modules via 'imports'
    # ...
}
```

### (Optional) Renaming a Machine

Older templates included static machine folders like `jon` and `sara`.
If your setup still uses such static machines, you can rename a machine folder to match your own machine name:

```bash
git mv ./machines/jon ./machines/<your-machine-name>
```

Since your Clan configuration lives inside a Git repository, remember:

* Only files tracked by Git (`git add`) are recognized.
* Whenever you add, rename, or remove files, run:

```bash
git add ./machines/<your-machine-name>
```

to stage the changes.

---

### (Optional) Removing a Machine

If you want to work with a single machine for now, you can remove other machine entries both from your `flake.nix` and from the `machines` directory. For example, to remove the machine `sara`:

```bash
git rm -rf ./machines/sara
```

Make sure to also remove or update any references to that machine in your `nix files` or `inventory.json` if you have any of that
