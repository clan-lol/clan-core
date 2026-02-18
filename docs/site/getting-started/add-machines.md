## Summary

Register machines in your Clan so they can be deployed to target devices.

## Requirements

- A Clan created during the previous step
- direnv running in your Clan folder

## Creating a Machine

```bash
clan machines create server
```

A dedicated folder will be created at `machines/server`.
You can see the complete [list](../guides/inventory/autoincludes.md) of auto-loaded files in our extended documentation.


### Configuring a Machine

You can edit your `clan.nix` file for additional machine features.
This example demonstrates a setup with two machines and a few extra settings:

```{.nix .annotate title="clan.nix" hl_lines="3-7 15-19"}
{
  inventory.machines = {
      server = {
          deploy.targetHost = "root@192.168.XXX.XXX";
          # Define tags here (optional)
          tags = [ ];
      };
      laptop = {
          # Define tags here (optional)
          tags = [ ];
      };
  };
  # Additional nixosConfiguration can also go in /machines/server/configuration.nix (autoloaded)
  machines = {
      server = { config, pkgs, ... }: {
          users.users.root.openssh.authorizedKeys.keys = [
              "ssh-ed25519 AAAAC3NzaC…"
          ];
      };
  };
}
```
inventory.machines: Tags can be used to automatically assign services to a machine later on (don't worry, we don't need to set this now). Additional machines - like laptop in this example - will all be listed here if created via `clan machines create $MACHINE_NAME`

machines: It is advised to add the *SSH key* of your setup device's root user here - That will ensure you can always login to your new machine via `ssh root@ip` from your setup device in case something goes wrong.

!!! Developer "Developer Note"
    The option: `inventory.machines.$MACHINE_NAME` is used to define metadata about the machine.

    That includes for example `deploy.targethost` or `machineClass` or `tags`

    The option: `machines.$MACHINE_NAME` is used to add extra *nixosConfiguration* to a machine



### (Optional) Manually Create a `configuration.nix` instead

<details>
  <summary>You can create the configuration file manually if you don't want to use the CLI commands</summary>

```nix title="./machines/server/configuration.nix"
{
    imports = [
        # enables GNOME desktop (optional)
        ../../modules/gnome.nix
    ];

    # Set nixosOptions here
    # Or import your own modules via 'imports'
}
```
</details>


### (Optional) Removing a Machine

<details>
  <summary>If you need to delete a machine...</summary>
...you can remove the entries both from your flake.nix and from the machines directory. For example, to remove laptop, use:

```bash
git rm -rf ./machines/laptop
```

Make sure to also remove or update any references to that machine in your Nix files and inventory.json

</details>


## Checkpoint

Verify that your machines have been created successfully by listing them:

```bash
clan machines list
```

This should display all the machines you've created (e.g., `server`). If you don't see your machines listed, double-check the previous steps.


## Up Next

In the next step, we will create and configure the users for the machines we just prepared.
