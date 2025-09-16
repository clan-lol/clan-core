# ClanLib

This folder is supposed to contain clan specific nix functions.

Such as:

- clan function
- select
- inventory function
- json-schema-converter

## Structure

Similar to `nixpkgs/lib` this produces a recursive attribute set in a fixed-point.
Functions within lib can depend on each other to create new abstractions.

### Conventions

Note: This is not consistently enforced yet.
If you start a new feature, or refactoring/touching existing ones, please help us to move towards the below illustrated.

A single feature-set/module may be organized like this:

```nix
#     ↓ The final clanLib
{lib, clanLib, ...}:
# ↓ portion to add to clanLib
{
    inventory.resolveTags = tags: inventory.machines; # implementation
    inventory.buildMachines = x: clanLib.inventory.resolveTags x; # implementation
}
```

Every bigger feature should live in a subfolder with the feature name.
It should contain two files:

- `default.nix`
- `test.nix`
- Everything else may be adopted as needed.

```
Example filetree
```
```sh
.
├── default.nix
├── clan
│   ├── default.nix
│   └── test.nix
└── inventory
    ├── services-subfeature
    │   ├── default.nix
    │   └── test.nix
    ├── instances-subfeature # <- We immediately see that this feature is not tested on itself.
    │   └── default.nix
    ├── default.nix
    └── test.nix
```

## Testing

For testing we use [nix-unit](https://github.com/nix-community/nix-unit)
