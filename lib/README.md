# ClanLib

This folder is supposed to contain clan specific nix functions.

Such as:

- build-clan function
- select
- build-inventory function
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

- `impl.nix`
- `test.nix`
- Everything else may be adopted as needed.

```
Example filetree
```
```sh
.
├── default.nix
├── build-clan
│   ├── impl.nix
│   └── test.nix
└── inventory
    ├── impl.nix
    ├── services-subfeature
    │   ├── impl.nix
    │   └── test.nix
    ├── instances-subfeature # <- We immediately see that this feature is not tested on itself.
    │   └── impl.nix
    └── test.nix
```

```nix
# default.nix
{lib, clanLib, ...}:
{
    inventory.resolveTags = import ./resolveTags { inherit lib clanLib; };
}
```

## Testing

For testing we use [nix-unit](https://github.com/nix-community/nix-unit)

TODO: define a helper that automatically hooks up `tests` in `flake.legacyPackages` and a corresponding buildable `checks` attribute
