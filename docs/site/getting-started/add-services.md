A service in clan is a self-contained, reusable unit of system configuration that provides a specific piece of functionality across one or more machines.

Think of it as a recipe for running a tool — like automatic backups, VPN networking, monitoring, etc.

In Clan Services are multi-Host & role-based:

- Roles map machines to logical service responsibilities, enabling structured, clean deployments.

- You can use tags instead of explicit machine names.

To learn more: [Guide about clanService](../guides/services/introduction-to-services.md)

!!! Important
    It is recommended to add at least one networking service such as `zerotier` that allows to reach all your clan machines from your setup computer across the globe.

## Configure a Zerotier Network (recommended)

```{.nix title="clan.nix" hl_lines="8-16"}
{
    inventory.machines = {
        jon = { };
        sara = { };
    };

    inventory.instances = {
        zerotier = { # (1)
            # Replace with the name (string) of your machine that you will use as zerotier-controller
            # See: https://docs.zerotier.com/controller/
            # Deploy this machine first to create the network secrets
            roles.controller.machines."jon" = { }; # (2)
            # Peers of the network
            # this line means 'all' clan machines will be 'peers'
            roles.peer.tags.all = { }; # (3)
        };
    };
    # ...
    # elided
}
```

1. See [services/official](../services/official/index.md) for all available services and how to configure them.
   Or read [guides/services](../guides/services/community.md) if you want to bring your own

2. Replace `__YOUR_CONTROLLER_` with the *name* of your machine.

3. This line will add all machines of your clan as `peer` to zerotier

## Adding more recommended defaults

Adding the following services is recommended for most users:

```{.nix title="clan.nix" hl_lines="7-14"}
{
    inventory.machines = {
        jon = { };
        sara = { };
    };
    inventory.instances = {
        admin = { # (1)
            roles.default.tags.all = { };
            roles.default.settings = {
                allowedKeys = {
                    "my-user" = "ssh-ed25519 AAAAC3N..."; # (2)
                };
            };
        };
        # ...
        # elided
    };
}
```

1. The `admin` service will generate a **root-password** and **add your ssh-key** that allows for convienient administration.
2. Equivalent to directly setting `authorizedKeys` like in [configuring a machine](../getting-started/add-machines.md#configuring-a-machine)
3. Adds `user = jon` as a user on all machines. Will create a `home` directory, and prompt for a password before deployment.
