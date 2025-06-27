
Clan has two general methods of adding machines:

- **Automatic**: Detects every folder in the `machines` folder.
- **Declarative**: Explicit declarations in Nix.

## Automatic registration

Every folder `machines/{machineName}` will be registered automatically as a Clan machine.

!!! info "Automatically loaded files"

    The following files are loaded automatically for each Clan machine:

    - [x] `machines/{machineName}/configuration.nix`
    - [x] `machines/{machineName}/hardware-configuration.nix`
    - [x] `machines/{machineName}/facter.json` Automatically configured, for further information see [nixos-facter](https://clan.lol/blog/nixos-facter/)
    - [x] `machines/{machineName}/disko.nix` Automatically loaded, for further information see the [disko docs](https://github.com/nix-community/disko/blob/master/docs/quickstart.md).

## Manual declaration

Machines can be added via [`clan.inventory.machines`](../guides/inventory.md) or in `clan.machines`, which allows for defining NixOS options.

=== "**Individual Machine Configuration**"

    ```{.nix}
    clan-core.lib.clan {
        machines = {
            "jon" = {
                # Any valid nixos config
            };
        };
    }
    ```

=== "**Inventory Configuration**"

    ```{.nix}
    clan-core.lib.clan {
        inventory = {
            machines = {
                "jon" = {
                    # Inventory can set tags and other metadata
                    tags = [ "zone1" ];
                    deploy.targetHost = "root@jon";
                };
            };
        };
    }
    ```
