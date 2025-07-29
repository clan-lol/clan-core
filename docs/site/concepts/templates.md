# How Templates work

Clan offers the ability to use templates for creating different resources.
It comes with some `<builtin>` templates and discovers all exposed templates from its flake's `inputs`

For example one can list all current templates like this:

```shellSession
$ clan templates list
Available 'clan' templates
├── <builtin>
│   ├── default: Initialize a new clan flake
│   ├── flake-parts: Flake-parts
│   └── minimal: for clans managed via (G)UI
└── inputs.self:
    ├── default: Initialize a new clan flake
    ├── flake-parts: Flake-parts
    └── minimal: for clans managed via (G)UI
Available 'disko' templates
├── <builtin>
│   └── single-disk: A simple ext4 disk with a single partition
└── inputs.self:
    └── single-disk: A simple ext4 disk with a single partition
Available 'machine' templates
├── <builtin>
│   ├── demo-template: Demo machine for the CLAN project
│   ├── flash-installer: Initialize a new flash-installer machine
│   ├── new-machine: Initialize a new machine
│   └── test-morph-template: Morph a machine
└── inputs.self:
    ├── demo-template: Demo machine for the CLAN project
    ├── flash-installer: Initialize a new flash-installer machine
    ├── new-machine: Initialize a new machine
    └── test-morph-template: Morph a machine
```

## Using `<builtin>` Templates

Templates are referenced via the `--template` `selector`

clan-core ships its native/builtin templates. Those are referenced if the selector is a plain string ( without `#` or `./.` )

For example:

`clan flakes create --template=flake-parts`

would use the native `<builtin>.flake-parts` template

## Selectors follow nix flake `reference#attribute` syntax

Selectors follow a very similar pattern as Nix's native attribute selection behavior.

Just like `nix build .` would build `packages.x86-linux.default` of the flake in `./.`

`clan flakes create --template=.` would create a clan from your **local** `default` clan template (`templates.clan.default`).

In fact this command would be equivalent, just make it more explicit

`clan flakes create --template=.#clan.templates.clan.default` (explicit path)

## Remote templates

Just like with Nix you could specify a remote url or path to the flake containing the template

`clan flakes create --template=github:owner/repo#foo`

!!! Note "Implementation Note"
    Not all features of Nix's attribute selection are currently matched.
    There are minor differences in case of unexpected behavior please create an [issue](https://git.clan.lol/clan/clan-core/issues/new)
