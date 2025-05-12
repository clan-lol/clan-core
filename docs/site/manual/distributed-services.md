# Setting up `inventory.instances`

In Clan *distributed services* can be declaratively deployed using the `inventory.instances` attribute

First of all it might be needed to explain what we mean by the term *distributed service*

## What is considered a distributed service?

A **distributed service** is a system where multiple machines work together to provide a certain functionality, abstracting complexity and allowing for declarative configuration and management.

A VPN service in a closed mesh network is a good example of a distributed service — each machine needs to know the addresses and cryptographic keys of the other machines in advance to establish secure, direct connections, enabling private and encrypted communication without relying on a central server.

The term **Multi-host-service-abstractions** was introduced previously in the [nixus repository](https://github.com/infinisil/nixus) and represents a similar concept.

## How to use such a Service in Clan?

In clan everyone can provide services via modules. Those modules must be [`clan.service` modules](../authoring/clanServices/index.md).

To use a service you need to create an instance of it via the `clan.inventory.instances` attribute:
The source of the module must be specified as a simple string.

```nix
{
    inventory = {
        instances = {
            "my-vpn" = {
                # service source
                module.name = "zerotier";
                # ...
            };
        };
    };
}
```

After specifying the *service source* for an instance, the next step is to configure the service.
Services operate on a strict *role-based membership model*, meaning machines are added by assigning them specific *roles*.

The following example shows a *zerotier service* which consists of a `controller` and some `peer` machines.

```nix
{
    inventory = {
        instances = {
            "my-vpn" = {
                # service source
                module.name = "zerotier";
                roles.peer.machines = {
                    # Right side needs to be an attribute set. Its purpose will become clear later
                    "my-machine-name" = {};
                };
                roles.controller.machines = {
                    "some-server-name" = {};
                };
            };
        };
    };
}
```

The next step is optional for some services. It might be desired to pass some service specific settings.
Either to affect all machines of a given role, or to affect a very specific machine.
For example:

In ZeroTier, the `roles.peer.settings` could specify the allowed IP ranges.

The `roles.controller.settings` could define a how to manage dynamic IP assignments for devices that are not statically configured.

```nix
{
    inventory = {
        instances = {
            "my-vpn" = {
                # service source
                module.name = "zerotier";
                roles.peer.machines = {
                    # Right side needs to be an attribute set. Its purpose will become clear later
                    "my-machine-name" = {};
                };
                roles.peer.settings = {
                    # Allow all ranges
                    ipRanges = [ "all" ];
                };
                roles.controller.machines = {
                    "some-server-name" = {
                        settings = {
                            # Enable the dynamic IP controller feature on this machine only
                            dynamicIp.enable = true;
                        };
                    };
                };
            };
        };
    };
}
```

Following all the steps described will result in consistent machine configurations that can be *installed* or *updated* via the [Clan CLI](../reference/cli/index.md)

### Using `clan.modules` from other people (optional)

The following example shows how to use remote modules and configure them for use in your clan.

!!! Note
    Typically you would just use the `import` builtin. But we wanted to provide a json-compatible interface to allow for external API integrations.

```nix title="flake.nix"
{
  inputs = {
    # ...
    libstd.url = "github:libfoo/libfoo";
    # ...
  };

  outputs =
    inputs: flake-parts.lib.mkFlake { inherit inputs; } (
      {
        clan = {
            inventory.instances = {
                "my-foo" = {
                    # Imports clan.module."mod-A" from inputs.libstd
                    module.input = "libstd";
                    module.name = "mod-A";
                };
            };
        };
      }
    );
}
```
