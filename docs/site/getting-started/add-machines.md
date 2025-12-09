##Summary

In Clan, machines describe all client devices from cloud VMs to bare metal laptops and are defined using Nix code inside the flake.

The creation of machines will be the same process for all kinds of devices and only later branch into specific steps.

This general guide will navigate you through the machine creation.

When finishing it, you will have prepared at least one machine that can be rolled out to a target device in the next steps.


##Requirements

- Estimated time: 30min
- You have created a clan during the previous step
- You are logged in as root on your setup device
- direnv is running in your clan folder (see previous step for setup)


## Creating a Machine

Navigate to your clan folder and run the following command to create a machine for our test user Jon:

```nix
clan machines create jon-machine
```

A dedicated folder will be created at `machines/jon-machine`.
You can see the complete [list](../guides/inventory/autoincludes.md) of auto-loaded files in our extended documentation.


### Configuring a Machine

You can edit your `clan.nix` file for additional machine features.
This example demonstrates a setup with two machines and a few extra settings:

```{.nix .annotate title="clan.nix" hl_lines="3-7 15-19"}
{
    inventory.machines = {
        jon-machine = {
            deploy.targ	etHost = "root@192.168.0.2";
            # Define tags here (optional)
            tags = [ ]; 
        };
        sara-machine = {
            # Define tags here (optional)
            tags = [ ]; # 
        };
    };
    # Define additional nixosConfiguration here
    # Or in /machines/jon/configuration.nix (autoloaded)
    machines = {
        jon-machine = { config, pkgs, ... }: {
            users.users.root.openssh.authorizedKeys.keys = [
                "ssh-ed25519 AAAAC3NzaC..." # elided
            ];
        };
    };
}
```
inventory.machines: Tags can be used to automatically assign services to a machine later on (don't worry, we don't need to set this now). Additional machines - like sara-machine in this example - will all be listed here if created via `clan machines create <name>`

machines: It is advised to add the *ssh key* of your setup device's root user here - That will ensure you can always login to your new machine via `ssh root@ip` from your setup device in case something goes wrong.

!!! Developer "Developer Note"
    The option: `inventory.machines.<name>` is used to define metadata about the machine.

    That includes for example `deploy.targethost` or `machineClass` or `tags`

    The option: `machines.<name>` is used to add extra *nixosConfiguration* to a machine



### (Optional) Manually Create a `configuration.nix` instead

<details>
  <summary>You can create the configuration file manually if you don't want to use the cli commands</summary>

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
</details>


### (Optional) Removing a Machine

<details>
  <summary>If you need to delete a machine...</summary>
...you can remove the entries both from your flake.nix and from the machines directory. For example, to remove sara-machine, use:

```bash
git rm -rf ./machines/sara-machine
```

Make sure to also remove or update any references to that machine in your nix files and inventory.json 

</details>


## Checkpoint

!!! Warning "In Development"
    We are currently working on a command to test your setup up to this point.

    For now, please check manually if there is a new folder for every `create machine NAME` you entered.

    ```ls machines/```


## Next Up

In the next step, we will create and configure the users for the machines we just prepared.
