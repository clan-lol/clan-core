# Inventory

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
