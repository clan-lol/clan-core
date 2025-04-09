# Authoring a 'clan.service' module

!!! Tip
    This is the successor format to the older [clanModules](../legacyModules/index.md)

    While some features might still be missing we recommend to adapt this format early and give feedback.

## Service Module Specification

This section explains how to author a clan service module.
We discussed the initial architecture in [01-clan-service-modules](https://git.clan.lol/clan/clan-core/src/branch/main/decisions/01-ClanModules.md) and decided to rework the format as follows:

### A Minimal module

First of all we need to register our module into the `inventory.modules` attribute. Make sure to choose a unique name so the module doesn't have a name collision with any of the core modules.

While not required we recommend to prefix your module attribute name.

If you export the module from your flake, other people will be able to import it and use it within their clan.

i.e. `@hsjobeki/customNetworking`

```nix title="flake.nix"
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

## Using values from a NixOS machine inside the module

!!! Example "Experimental Status"
    This feature is experimental and should be used with care.

Sometimes a settings value depends on something within a machines `config`.

Since the `interface` is defined completely machine-agnostic this means values from a machine cannot be set in the traditional way.

The following example shows how to create a local instance of machine specific settings.

```nix title="someservice.nix"
{
    # Maps over all instances and produces one result per instance.
    perInstance = { instanceName, extendSettings, machine, roles, ... }: {
        nixosModule = { config, ... }:
          let
            # Create new settings with
            # 'ipRanges' defaulting to 'config.network.ip.range' from this machine
            # This only works if there is no 'default' already.
            localSettings = extendSettings {
                ipRanges = lib.mkDefault config.network.ip.range;
            };
          in
            {
                # ...
            };
    };
}
```

!!! Danger
    `localSettings` are a local attribute. Other machines cannot access it.
    If calling extendSettings is done that doesn't change the original `settings` this means if a different machine tries to access i.e `roles.client.settings` it would *NOT* contain your changes.

    Exposing the changed settings to other machines would come with a huge performance penalty, thats why we don't want to offer it.

## Passing `self` or `pkgs` to the module

Passing any dependencies in general must be done manually.

In general we found the following two best practices:

1. Using `lib.importApply`
2. Using a wrapper module

Both have pros and cons. After all using `importApply` is the easier one, but might be more limiting sometimes.

### Using `importApply`

Using [importApply](https://github.com/NixOS/nixpkgs/pull/230588) is essentially the same as `import file` followed by a function-application; but preserves the error location.

Imagine your module looks like this

```nix title="messaging.nix"
{ self }:
{ ... }: # This line is optional
{
    _class = "clan.service";
    manifest.name = "messaging"
    # ...
}
```

To import the module use `importApply`

```nix title="flake.nix"
# ...
outputs = inputs: flake-parts.lib.mkFlake { inherit inputs; } ({self, lib, ...}: {
    imports = [ inputs.clan-core.flakeModules.default ];
    # ...
    clan = {
        # Register the module
        inventory.modules."@hsjobeki/messaging" = lib.importApply ./service-modules/messaging.nix { inherit self; };

        # Expose the module for downstream users, 'self' would always point to this flake.
        modules."@hsjobeki/messaging" = lib.importApply ./service-modules/messaging.nix { inherit self; };
    };
})
```

### Using a wrapper module

```nix title="messaging.nix"
{ config, ... }:
{
    _class = "clan.service";
    manifest.name = "messaging"
    # ...
    # config.myClan
}
```

Then wrap the module and forward the variable `self` from the outer context into the module

```nix title="flake.nix"
# ...
outputs = inputs: flake-parts.lib.mkFlake { inherit inputs; } ({self, lib, ...}: {
    imports = [ inputs.clan-core.flakeModules.default ];
    # ...
    clan = {
        # Register the module
        inventory.modules."@hsjobeki/messaging" = {
            # Create an option 'myClan' and assign it to 'self'
            options.myClan = lib.mkOption {
                default = self;
            };
            imports = [./service-modules/messaging.nix ];
        }
    };
})
```

The benefit of this approach is that downstream users can override the value of `myClan` by using `mkForce` or other priority modifiers.
