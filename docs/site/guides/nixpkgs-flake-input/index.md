**Q**: How should I choose the nixpkgs input for my flake when using clan-core?

**A**: In general, you should pin your flake to a recent nixpkgs version.
There are two common ways to do this, each with its own trade-offs:

## Follow clan-core

- (+) Recommended for most people.
- (+) Verified by our CI and widely used by others
- (-) Coupling to version bumps in clan-core,
    - Upstream features and packages may take longer to land.

```nix
inputs = {
    clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    # Uses the nixpkgs version that was locked in clan-core
    nixpkgs.follows = "clan-core/nixpkgs";
}
```

## Use your own nixpkgs version

- (+) Faster access to new upstream features and packages
- (-) Recommended for advanced usage.
- (-) Not covered by our CI — you’re on the frontier

```nix
inputs = {
    # Use your own version here.
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
    # Uses the nixpkgs version of your own flake in clan-core
    clan-core.inputs.nixpkgs.follows = "nixpkgs";
}
```

## Recommended

To avoid ambiguity or incompatibility issues, it’s a good idea to check your `flake.lock` for duplicate `nixpkgs` entries.
This usually indicates that one of your flake inputs is missing a `follows` directive.

If you see something like this, it means you have multiple versions of `nixpkgs`:

```json
    "nixpkgs": {
      "locked": {
        "lastModified": 315532800,
        "narHash": "sha256-1tUpklZsKzMGI3gjo/dWD+hS8cf+5Jji8TF5Cfz7i3I=",
        "rev": "08b8f92ac6354983f5382124fef6006cade4a1c1",
        "type": "tarball",
        "url": "https://releases.nixos.org/nixpkgs/nixpkgs-25.11pre862603.08b8f92ac635/nixexprs.tar.xz"
      },
      "original": {
        "type": "tarball",
        "url": "https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz"
      }
    },
    "nixpkgs_2": {
      "locked": {
        "lastModified": 1758346548,
        "narHash": "sha256-afXE7AJ7MY6wY1pg/Y6UPHNYPy5GtUKeBkrZZ/gC71E=",
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
    },
```

You can grep through your lock file to locate which inputs are referencing the wrong nixpkgs.

In this example, `home-manager` is pointing to `nixpkgs_2` instead of the main `nixpkgs`

```json
    // ...
    "home-manager": {
      "inputs": {
        "nixpkgs": "nixpkgs_2"
      }
    // ...
```

To fix this add the following line to your flake.nix inputs:

```nix
home-manager.inputs.nixpkgs.follows = "nixpkgs";
```

Repeat this process until all duplicate `nixpkgs` entries are eliminated.

This helps prevent cross-version conflicts and ensures all inputs use the same `nixpkgs` source.
