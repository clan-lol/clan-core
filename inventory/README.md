# Inventory

The inventory is our concept for distributed services. Users can configure multiple machines with minimal effort.

- The inventory acts as a declarative source of truth for all machine configurations.
- Users can easily add or remove machines to/from services.
- Ensures that all machines and services are configured consistently, across multiple nixosConfigs.
- Defaults and predefined roles in our modules minimizes the need for manual configuration.

Open questions:

- [ ] How do we set default role, description and other metadata?
  - It must be accessible from Python.
  - It must set the value in the module system.

- [ ] Inventory might use assertions. Should each machine inherit the inventory assertions ?

- [ ] Is the service config interface the same as the module config interface ?

- [ ] As a user do I want to see borgbackup as the high level category?


Architecture

```
nixosConfig < machine_module        < inventory
---------------------------------------------
nixos   < borgbackup            <- inventory <-> UI

        creates the config      Maps from high level services to the borgbackup clan module
        for ONE machine         Inventory is completely serializable.
                                UI can interact with the inventory to define machines, and services
                                Defining Users is out of scope for the first prototype.
```

## Provides a specification for the inventory

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
