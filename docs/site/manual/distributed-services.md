# Services

First of all it might be needed to explain what we mean by the term *distributed service*

!!! Note
    Currently there are two ways of using such services.
    1. via `inventory.services` **Will be deprecated**
    2. via `inventory.instances` **Will be the new `inventory.services` once everyone has migrated**

## What is considered a service?

A **distributed service** is a system where multiple machines work together to provide a certain functionality, abstracting complexity and allowing for declarative configuration and management.

A VPN service in a closed mesh network is a good example of a distributed service — each machine needs to know the addresses and cryptographic keys of the other machines in advance to establish secure, direct connections, enabling private and encrypted communication without relying on a central server.

The term **Multi-host-service-abstractions** was introduced previously in the [nixus repository](https://github.com/infinisil/nixus) and represents a similar concept.

## How to use such a Service in Clan?

In clan everyone can provide services via modules. Those modules must comply to a certain [specification](#service-module-specification), which is discussed later.

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

## Service Module Specification

This section explains how to author a clan service module. As decided in [01-clan-service-modules](https://git.clan.lol/clan/clan-core/src/branch/main/decisions/01-ClanModules.md)

!!! Warning
    The described modules are fundamentally different to the existing [clanModules](../clanmodules/index.md)
    Most of the clanModules will be migrated into the described format. We actively seek for contributions here.

### Minimal module

!!! Tip
    Unlike previously modules can now be inlined. There is no file-system structure needed anymore.

First of all we need to hook our module into the `inventory.modules` attribute. Make sure to choose a unique name so the module doesn't have a name collision with any of the core modules.

While not required we recommend to prefix your module attribute name.

If you export the module from your flake, other people will be able to import it and use it within their clan.

i.e. `@hsjobeki/customNetworking`

```nix title=flake.nix
# ...

outputs = inputs: flake-parts.lib.mkFlake { inherit inputs; } ({
    imports = [ inputs.clan-core.flakeModules.default ];
    # ...
    clan = {
        inventory = {
            # We could also inline the complete module spec here
            # For example
            # {...}: { _class = "clan.service"; ... };
            modules."@hsjobeki/customNetworking" = import ./service-modules/networking.nix;
        };

        # If needed: Exporting the module for other people
        modules."@hsjobeki/customNetworking" = import ./service-modules/networking.nix;
    };
})
```

The imported module file must fulfill at least the following requirements:

- Be an actual module. That means: Be either an attribute set; or a function that returns an attribute set.
- Required `_class = "clan.service"
- Required `manifest.name = "<name of the provided service>"`

```nix title="/service-modules/networking.nix"
{
    _class = "clan.service";
    manifest.name = "zerotier-networking";
    # ...
}
```

### Adding functionality to the module

While the very minimal module is valid in itself it has no way of adding any machines to it, because it doesn't specify any roles.

The next logical step is to think about the interactions between the machines and define *roles* for them.

Here is a short guide with some conventions:

- [ ] If they all have the same relation to each other `peer` is commonly used. `peers` can often talk to each other directly.
- [ ] Often machines don't necessarily have direct relation to each other and there is one elevated machine in the middle classically know as `client-server`. `clients` are less likely to talk directly to each other than `peers`
- [ ] If your machines don't have any relation and/or interactions to each other you should reconsider if the desired functionality is really a multi-host service.

```nix title="/service-modules/networking.nix"
{
    _class = "clan.service";
    manifest.name = "zerotier-networking";

    # Define what roles exist
    roles.peer = {};
    roles.controller = {};
    # ...
}
```

Next we need to define the settings and the behavior of these distinct roles.

```nix title="/service-modules/networking.nix"
{
    _class = "clan.service";
    manifest.name = "zerotier-networking";

    # Define what roles exist
    roles.peer = {
        interface = {
            # These options can be set via 'roles.client.settings'
            options.ipRanges = mkOption { type = listOf str; };
        };

        # Maps over all instances and produces one result per instance.
        perInstance = { instanceName, settings, machine, roles, ... }: {
        # Analog to 'perSystem' of flake-parts.
            # For every instance of this service we will add a nixosModule to a client-machine
            nixosModule = { config, ... }: {
                # Interaction examples what you could do here:
                # - Get some settings of this machine
                # settings.ipRanges
                #
                # - Get all controller names:
                # allControllerNames = lib.attrNames roles.controller.machines
                #
                # - Get all roles of the machine:
                # machine.roles
                #
                # - Get the settings that where applied to a specific controller machine:
                # roles.controller.machines.jon.settings
                #
                # Add one systemd service for every instance
                systemd.services.zerotier-client-${instanceName} = {
                    # ... depend on the '.config' and 'perInstance arguments'
                };
            };
        }
    };
    roles.controller = {
        interface = {
            # These options can be set via 'roles.server.settings'
            options.dynamicIp.enable = mkOption { type = bool; };
        };
        perInstance = { ... }: {};
    };

    # Maps over all machines and produces one result per machine.
    perMachine = { instances, machine, ... }: {
    # Analog to 'perSystem' of flake-parts.
        # For every machine of this service we will add exactly one nixosModule to a machine
        nixosModule = { config, ... }: {
            # Interaction examples what you could do here:
            # - Get the name of this machine
            # machine.name
            #
            # - Get all roles of this machine across all instances:
            # machine.roles
            #
            # - Get the settings of a specific instance of a specific machine
            # instances.foo.roles.peer.machines.jon.settings
            #
            # Globally enable something
            networking.enable = true;
        };
    };
    # ...
}
```
