# Nixpkgs Flake Input

Your flake needs a `nixpkgs` input, and the version you pick affects which packages you get and whether Clan's CI has tested your combination. This guide shows you how to choose one, how to avoid duplicate versions sneaking into your lockfile, and how to patch individual packages with overlays.

## Choose a nixpkgs version

There are two sensible options. Pick the first unless you have a reason not to.

### Option 1: Follow clan-core (recommended)

Use the `nixpkgs` version that Clan's CI already tests against:

```nix
inputs = {
  clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  nixpkgs.follows = "clan-core/nixpkgs";
};
```

This pins your flake to the same `nixpkgs` revision that `clan-core` pins. Every `clan-core` update brings a matching `nixpkgs` update, so you stay on a combination that has been verified end-to-end. The trade-off is that new upstream packages only reach you when `clan-core` bumps its input.

### Option 2: Track your own nixpkgs

Pin `nixpkgs` yourself and make `clan-core` follow it:

```nix
inputs = {
  nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  clan-core.inputs.nixpkgs.follows = "nixpkgs";
};
```

This gives you faster access to upstream changes, at the cost of running a combination that Clan's CI does not cover. Use it if you need a package or fix that has not yet landed in the version `clan-core` follows.

## Check for duplicate nixpkgs entries

Even with `follows` set up correctly, a transitive input can still pull in its own `nixpkgs`. When that happens, your `flake.lock` ends up with more than one `nixpkgs` entry and you evaluate the same package tree twice.

Look at `flake.lock`. If you see two entries like this, you have a duplicate:

```json
"nixpkgs": {
  "locked": {
    "rev": "08b8f92ac6354983f5382124fef6006cade4a1c1",
    "type": "tarball",
    "url": "https://releases.nixos.org/nixpkgs/nixpkgs-25.11pre862603.08b8f92ac635/nixexprs.tar.xz"
  }
},
"nixpkgs_2": {
  "locked": {
    "owner": "nixos",
    "repo": "nixpkgs",
    "rev": "b2a3852bd078e68dd2b3dfa8c00c67af1f0a7d20",
    "type": "github"
  },
  "original": {
    "owner": "nixos",
    "ref": "nixos-25.05",
    "repo": "nixpkgs",
    "type": "github"
  }
}
```

The second entry is the one another input brought in. To find which input is responsible, search `flake.lock` for `nixpkgs_2`. You will usually find something like this:

```json
"home-manager": {
  "inputs": {
    "nixpkgs": "nixpkgs_2"
  }
}
```

That tells you `home-manager` is the culprit. Add a `follows` line for it in your `flake.nix`:

```nix
home-manager.inputs.nixpkgs.follows = "nixpkgs";
```

This points `home-manager` at your main `nixpkgs` instead of its own. Repeat the search for any remaining `nixpkgs_3`, `nixpkgs_4`, and so on until `flake.lock` has only one `nixpkgs` entry.

:::admonition[Tip]{type=tip}
Run `nix flake update` after adding a `follows` line so the lockfile picks up the change.
:::

## Customise packages with overlays

If you need to patch a package that already exists in `nixpkgs`, use an [overlay](https://wiki.nixos.org/wiki/Overlays). Overlays are the right tool for modifying existing packages. If you want to add a brand-new package of your own, see the [Clan templates](https://git.clan.lol/clan/clan-core/src/branch/main/templates) instead.

Here is a `flake.nix` that wires an overlay into the `pkgs` that Clan uses:

```nix [flake.nix]
{
  inputs.clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  inputs.nixpkgs.follows = "clan-core/nixpkgs";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  inputs.flake-parts.inputs.nixpkgs-lib.follows = "clan-core/nixpkgs";

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      imports = [
        inputs.clan-core.flakeModules.default
      ];

      clan = {
        imports = [ ./clan.nix ];
      };

      perSystem =
        { system, ... }:
        {
          _module.args.pkgs = import inputs.nixpkgs {
            inherit system;
            overlays = [
              inputs.foo.overlays.default
              (final: prev: {
                # ... things you need to patch ...
              })
            ];
            config.allowUnfree = true;
          };
        };
    };
}
```

The `perSystem` block builds a custom `pkgs` by importing `nixpkgs` with your overlays applied, and hands it back to the module system through `_module.args.pkgs`. From that point on, every Clan module in your flake sees the patched package set. The first overlay in the list comes from another flake input (`inputs.foo`); the second is an inline overlay where you can override individual packages directly. Set `config.allowUnfree = true` if you need packages with non-free licences.

For more complete examples, see the [Clan templates](https://git.clan.lol/clan/clan-core/src/branch/main/templates).
