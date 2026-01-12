## Summary

A service in clan is a self-contained, reusable unit of system configuration that provides a specific piece of functionality across one or more machines.

Think of it as a recipe for running a tool — like automatic backups, VPN networking, monitoring, etc.

In Clan, services are multi-host and role-based:

- Roles map machines to logical service responsibilities, enabling structured and clean deployments.

- You can use tags instead of explicit machine names.

In this step of the guide, we will add two of the most frequently used services to your new setup: Networking and ssh.

To learn more about services in general, visit [Clan Services](../guides/services/introduction-to-services.md)

!!! Important
    It is recommended to always add at least one networking service such as `zerotier` that can reach all your clan machines from your setup computer. We will do so in the following steps.


## Requirements

- Estimated time: 15 minutes

- A Clan with at least one machine and at least one user prepared as described in the previous steps


## Configure a ZeroTier Network

Add the configuration for a ZeroTier Network to your clan.nix file as follows:

```{.nix title="clan.nix" hl_lines="8-16"}
{
  inventory.machines = {
    jon-machine = { };
    sara-machine = { };
  };

  inventory.instances = {
    zerotier = { 
      # Replace with the name (string) of your machine that you will use as zerotier-controller
      # See: https://docs.zerotier.com/controller/
      # Deploy this machine first to create the network secrets
      roles.controller.machines."jon-machine" = { }; #edit your machine name
      # Peers of the network
      # this line means 'all' clan machines will be 'peers'
      roles.peer.tags.all = { }; 
    };
  };
  # ...
  # elided
}
```

See [services/official](../services/definition.md) for all available services and how to configure them.

Or read [guides/services](../guides/services/community.md) if you want to bring your own!


## Adding more recommended defaults: SSH Access

Adding ssh keys is one of the most recommended services:

```{.nix title="clan.nix" hl_lines="7-14"}
{
    inventory.machines = {
        jon-machine = { };
        sara-machine = { };
    };
    inventory.instances = {
        admin = { 
            roles.default.tags.all = { };
            roles.default.settings = {
                allowedKeys = {
                    "root" = "ssh-ed25519 AAAAC3N...";  
                };
            };
        };
        # ...
        # elided
    };
}
```

The `admin` service will generate a **root-password** and **add your ssh-key** that allows for convenient administration to all machines.

This method is equivalent to directly setting `authorizedKeys` like in [configuring a machine](../getting-started/add-machines.md#configuring-a-machine)


## Checkpoint

!!! Warning "Under Construction"
    We are working on a feasible solution to test your progress up to this point.
    Unfortunately, there are currently no checkpoints available.


## Up Next

We will deploy your configuration to either a bare metal physical machine or a virtual machine.

Please select your path accordingly:

[Next Step: Prepare Physical Machines](prepare-physical-machines.md){ .md-button .md-button--primary }

[Next Step: Prepare Virtual Machines](prepare-virtual-machines.md){ .md-button .md-button--primary }

You can have a mix of both if you like. In that case, simply follow the respective guide per machine type.
