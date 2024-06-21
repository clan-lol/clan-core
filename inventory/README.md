# Inventory

The inventory is our concept for distributed services. Users can configure multiple machines with minimal effort.

- The inventory acts as a declarative source of truth for all machine configurations.
- Users can easily add or remove machines to/from services.
- Ensures that all machines and services are configured consistently, across multiple nixosConfigs.
- Defaults and predefined roles in our modules minimizes the need for manual configuration.

Design questions:

- [ ] Is the service config interface the same as the module config interface ?

- [ ] As a user i dont want to see borgbackup as the high level category ?

- [x] Must roles be a list ?
    -> Yes. In zerotier a machine can be "moon" and "controller" at the same time.

- [x] Is role client different from peer ? Do we have one example where we use client and peer together and they are different?
    -> There are many roles. And they depend on the service.

- [x] Should we use the module name in the path of the service?
    -> YES
    ```json
    // ${module_name}.${instance_name}
    services.borgbackup-static.backup1 = {

    }
    ```

    Pro:
        Easier to handle.
        Better groups the module specific instances.
    Contra:
        More nesting in json

    Neutral: Module name is hard to change. Exists anyways.

- [x] Should the machine specific service config be part of the service?
    -> NO. because ...
    - The config implements the schema of the module, which is declared in the service.
    - If the config is placed in the machine, it becomes unclear that the scope is ONLY the service and NOT the global nixos config.
    - If the config is placed in the machine it is de-located into another top-level field. In the module this complicates access.

Architecture

```
nixosConfig < machine_module        < inventory
---------------------------------------------
nixos   < borgbackup            + borgbackup-static > UI

        creates the config      Maps from high level services to the borgbackup clan module
        for ONE machine
```

- [ ] Why do we need 2 modules?
    -> It is technically possible to have only 1 module.
    Pros:
        Simple to use/Easy to understand.
        Less modules
    Cons:
        Harder to write a module. Because it must do 2 things.
        One module should do only 1 thing.

```nix
clan.machines.${machine_name} = {
    # "borgbackup.ssh.pub" = machineDir + machines + "/facts/borgbackup.ssh.pub";
    facts = ...
};
clan.services.${instance} = {
#   roles.server = [ "jon_machine" ]
#   roles.${role_name} = [ ${machine_name} ];
};
```

This part provides a specification for the inventory.

It is used for design phase and as validation helper.

> Cue is less verbose and easier to understand and maintain than json-schema.
> Json-schema, if needed can be easily generated on-the fly.

## Checking validity

Directly check a json against the schema

`cue vet inventory.json root.cue -d '#Root'`

## Json schema

Export the json-schema i.e. for usage in python / javascript / nix

`cue export --out openapi root.cue`

## Usage

Comments are rendered as descriptions in the json schema.

```cue
// A name of the clan (primarily shown by the UI)
name: string
```

Cue open sets. In the following `foo = {...}` means that the key `foo` can contain any arbitrary json object.

```cue
foo: { ... }
```

Cue dynamic keys.

```cue
[string]: {
    attr: string
}
```

This is the schema of

```json
{
    "a": {
        "attr": "foo"
    },
    "b": {
        "attr": "bar"
    }
    // ... Indefinitely more dynamic keys of type "string"
}
```
