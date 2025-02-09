# Clan service modules

Status: Accepted

## Context

To define a service in Clan, you need to define two things:

- `clanModule` - defined by module authors
- `inventory` - defined by users

The `clanModule` is currently a plain NixOS module. It is conditionally imported into each machine depending on the `service` and `role`.

A `role` is a function of a machine within a service. For example in the `backup` service there are `client` and `server` roles.

The `inventory` contains the settings for the user/consumer of the module. It describes what `services` run on each machine and with which `roles`.

Additionally any `service` can be instantiated multiple times.

This ADR proposes that we change how to write a `clanModule`. The `inventory` should get a new attribute called `instances` that allow for configuration of these modules.

### Status Quo

In this example the user configures 2 instances of the `networking` service:

The *user* defines

```nix
{
  inventory.services = {
    # anything inside an instance is instance specific
    networking."instance1" = {
      roles.client.tags = [ "all" ];
      machines.foo.config = { ... /* machine specific settings */ };

      # this will not apply to `clients` outside of `instance1`
      roles.client.config = { ... /* client specific settings */ };
    };
    networking."instance2" = {
      roles.server.tags = [ "all" ];
      config = { ... /* applies to every machine that runs this instance */ };
    };
  };
}
```

The *module author* defines:

```nix
# networking/roles/client.nix
{ config, ... }:
let
  instances = config.clan.inventory.services.networking or { };

  serviceConfig = config.clan.networking;
in {
  ## Set some nixos options
}
```

### Problems

Problems with the current way of writing clanModules:

1. No way to retrieve the config of a single service instance, together with its name.
2. Directly exporting a single, anonymous nixosModule without any intermediary attribute layers doesn't leave room for exporting other inventory resources such as potentially `vars` or `homeManagerConfig`.
3. Can't access multiple config instances individually.
   Example:
   ```nix
   inventory = {
      services = {
        network.c-base = {
          instanceConfig.ips = {
            mors = "172.139.0.2";
          };
        };
        network.gg23 = {
          instanceConfig.ips = {
            mors = "10.23.0.2";
          };
        };
      };
    };
   ```
   This doesn't work because all instance configs are applied to the same namespace. So this results in a conflict currently.
   Resolving this problem means that new inventory modules cannot be plain nixos modules anymore. If they are configured via `instances` / `instanceConfig` they cannot be configured without using the inventory. (There might be ways to inject instanceConfig but that requires knowledge of inventory internals)

4. Writing modules for multiple instances is cumbersome. Currently the clanModule author has to write one or multiple `fold` operations for potentially every nixos option to define how multiple service instances merge into every single one option. The new idea behind this adr is to pull the common fold function into the outer context provide it as a common helper. (See the example below. `perInstance` analog to the well known `perSystem` of flake-parts)

5. Each role has a different interface. We need to render that interface into json-schema which includes creating an unnecessary test machine currently. Defining the interface at a higher level (outside of any machine context) allows faster evaluation and an isolation by design from any machine.
This allows rendering the UI (options tree) of a service by just knowing the service and the corresponding roles without creating a dummy machine.

6. The interface of defining config is wrong. It is possible to define config that applies to multiple machine at once. It is possible to define config that applies to
a machine as a hole. But this is wrong behavior because the options exist at the role level. So config must also always exist at the role level.
Currently we merge options and config together but that may produce conflicts. Those module system conflicts are very hard to foresee since they depend on what roles exist at runtime.

## Proposed Change

We will create a new module class which is defined by `_class = "clan.service"` ([documented here](https://nixos.org/manual/nixpkgs/stable/#module-system-lib-evalModules-param-class)).

Existing clan modules will still work by continuing to be plain NixOS modules. All new modules can set `_class = "clan.service";` to use the proposed features.

In short the change introduces a new module class that makes the currently necessary folding of `clan.service`s `instances` and `roles` a common operation. The module author can define the inner function of the fold operations which is called a `clan.service` module.

There are the following attributes of such a module:

### `roles.<roleName>.interface`

Each role can have a different interface for how to be configured.
I.e.: A `client` role might have different options than a `server` role.

This attribute should be used to define `options`. (Not `config` !)

The end-user defines the corresponding `config`.

This submodule will be evaluated for each `instance role` combination and passed as argument into `perInstance`.

This submodules `options` will be evaluated to build the UI for that module dynamically.

### **Result attributes**

Some common result attributes are produced by modules of this proposal, those will be referenced later in this document but are commonly defined as:

- `nixosModule` A single nixos module. (`{config, ...}:{ environment.systemPackages = []; }`)
- `services.<serviceName>` An attribute set of `_class = clan.service`. Which contain the same thing as this whole ADR proposes.
- `vars` To be defined. Reserved for now.

### `roles.<roleName>.perInstance`

This acts like a function that maps over all `service instances` of a given `role`.
It produces the previously defined **result attributes**.

I.e. This allows to produce multiple `nixosModules` one for every instance of the service.
Hence making multiple `service instances` convenient by leveraging the module-system merge behavior.

### `perMachine`

This acts like a function that maps over all `machines` of a given `service`.
It produces the previously defined **result attributes**.

I.e. this allows to produce exactly one `nixosModule` per `service`.
Making it easy to set nixos-options only once if they have a one-to-one relation to a service being enabled.

Note: `lib.mkIf` can be used on i.e. `roleName` to make the scope more specific.

### `services.<serviceName>`

This allows to define nested services.
i.e the *service* `backup` might define a nested *service* `ssh` which sets up an ssh connection.

This can be defined in `perMachine` and `perInstance`

- For Every `instance` a given `service` may add multiple nested `services`.
- A given `service` may add a static set of nested `services`; Even if there are multiple instances of the same given service.

Q: Why is this not a top-level attribute?
A: Because nested service definitions may also depend on a `role` which must be resolved depending on `machine` and `instance`. The top-level module doesn't know anything about machines. Keeping the service layer machine agnostic allows us to build the UI for a module without adding any machines. (One of the problems with the current system)

```
zerotier/default.nix
```
```nix
# Some example module
{
  _class = "clan.service";

  # Analog to flake-parts 'perSystem' only that it takes instance
  # The exact arguments will be specified and documented along with the actual implementation.
  roles.client.perInstance = {
      # attrs : settings of that instance
      settings,
      # string : name of the instance
      instanceName,
      # { name :: string , roles :: listOf string; }
      machine,
      # { {roleName} :: { machines :: listOf string; } }
      roles,
      ...
    }:
    {
      # Return a nixos module for every instance.
      # The module author must be aware that this may return multiple modules (one for every instance) which are merged natively
      nixosModule = {
        config.debug."${instanceName}-client" = instanceConfig;
      };
    };
  # Function that is called once for every machine with the role "client"
  # Receives at least the following parameters:
  #
  # machine :: { name :: String, roles :: listOf string; }
  # Name of the machine
  #
  # instances :: { instanceName :: { roleName :: { machines :: [ string ]; }}}
  # Resolved roles
  # Same type as currently in `clan.inventory.services.<ServiceName>.<InstanceName>.roles`
  #
  # The exact arguments will be specified and documented along with the actual implementation.
  perMachine = {machine, instances, ... }: {
    nixosModule =
      { lib, ... }:
      {
        # Some shared code should be put into a shared file
        # Which is then imported into all/some roles
        imports = [
          ../shared.nix
        ] ++
        (lib.optional (builtins.elem "client" machine.roles)
        {
          options.debug = lib.mkOption {
            type = lib.types.attrsOf lib.types.raw;
          };
        });
      };
  };
}
```

## Inventory.instances

This document also proposes to add a new attribute to the inventory that allow for exclusive configuration of the new modules.
This allows to better separate the new and the old way of writing and configuring modules. Keeping the new implementation more focussed and keeping existing technical debt out from the beginning.

The following thoughts went into this:

- Getting rid of `<serviceName>`: Using only the attribute name (plain string) is not sufficient for defining the source of the service module. Encoding meta information into it would also require some extensible format specification and parser.
- removing instanceConfig and machineConfig: There is no such config. Service configuration must always be role specific, because the options are defined on the role.
- renaming `config` to `settings` or similar. Since `config` is a module system internal name.
- Tags and machines should be an attribute set to allow setting `settings` on that level instead.

```nix
{
  inventory.instances = {
    "instance1" = {
      # Allows to define where the module should be imported from.
      module = {
        input = "clan-core";
        name = "borgbackup";
      };
      # settings that apply to all client machines
      roles.client.settings = {};
      # settings that apply to the client service of machine with name <machineName>
      # There might be a server service that takes different settings on the same machine!
      roles.client.machines.<machineName>.settings = {};
      # settings that apply to all client-instances with tag <tagName>
      roles.client.tags.<tagName>.settings = {};
    };
    "instance2" = {
      # ...
    };
  };
}

```

## Iteration note

We want to implement the system as described. Once we have sufficient data on real world use-cases and modules we might revisit this document along with the updated implementation.
