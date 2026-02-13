## Summary

Give your Clan networking and SSH access so your devices can reach each other and you can administer them remotely.

Both are configured as Clan services: self-contained units of configuration that you assign to machines via roles and tags.

To learn more about services in general, visit [Clan Services](../guides/services/introduction-to-services.md)

!!! Important
It is recommended to always add at least one networking service such as `zerotier` that can reach all your Clan machines from your Setup Device. We will do so in the following steps.

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
      roles.controller.machines."jon-machine" = { };
      # All clan machines will be peers of the network
      roles.peer.tags.all = { };
    };
  };
}
```

See [services/official](../services/definition.md) for all available services and how to configure them.

Or read [guides/services](../guides/services/community.md) if you want to bring your own!

## Adding more recommended defaults: SSH Access

Adding SSH keys is one of the most recommended services:

```{.nix title="clan.nix" hl_lines="7-26"}
{
    inventory.machines = {
        jon-machine = { };
        sara-machine = { };
    };
    inventory.instances = {
        sshd = {
            roles.server.tags.all = { };
            roles.server.settings.authorizedKeys = {
                "root" = "ssh-ed25519 AAAAC3N…";
            };
        };

        user-root = {
            module = {
                name = "users";
                input = "clan-core";
            };
            roles.default.tags.all = { };
            roles.default.settings = {
                user = "root";
                prompt = true;
            };
        };
    };
}
```

The `sshd` service will **add your SSH key** for remote access to all machines. The `user-root` service will generate a **root password** for convenient administration.

This method is equivalent to directly setting `authorizedKeys` like in [configuring a machine](../getting-started/add-machines.md#configuring-a-machine)

## Checkpoint

!!! Warning "Under Construction"
We are working on a feasible solution to test your progress up to this point.
Unfortunately, there are currently no checkpoints available.

## Up Next

We will deploy your configuration to either a bare metal physical device or a virtual device.

Please select your path accordingly:

[Next Step: Prepare Physical Machines](./prepare-physical-machines.md){ .md-button .md-button--primary }

[Next Step: Prepare Virtual Machines](./prepare-virtual-machines.md){ .md-button .md-button--primary }

You can have a mix of both if you like. In that case, simply follow the respective guide per device type.
