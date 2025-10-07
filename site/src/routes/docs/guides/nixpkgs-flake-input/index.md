**Q**: How should I choose the `nixpkgs` input for my flake when using `clan-core`?

**A**: Pin your flake to a recent `nixpkgs` version. Here are two common approaches, each with its trade-offs:

## Option 1: Follow `clan-core`

- **Pros**:
  - Recommended for most users.
  - Verified by our CI and widely used by others.
- **Cons**:
  - Coupled to version bumps in `clan-core`.
  - Upstream features and packages may take longer to land.

Example:

```nix
inputs = {
  clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  # Use the `nixpkgs` version locked in `clan-core`
  nixpkgs.follows = "clan-core/nixpkgs";
};
```

## Option 2: Use Your Own `nixpkgs` Version

- **Pros**:
  - Faster access to new upstream features and packages.
- **Cons**:
  - Recommended for advanced users.
  - Not covered by our CI — you’re on the frontier.

Example:

```nix
inputs = {
  # Specify your own `nixpkgs` version
  nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  clan-core.url = "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  # Ensure `clan-core` uses your `nixpkgs` version
  clan-core.inputs.nixpkgs.follows = "nixpkgs";
};
```

## Recommended: Avoid Duplicate `nixpkgs` Entries

To prevent ambiguity or compatibility issues, check your `flake.lock` for duplicate `nixpkgs` entries. Duplicate entries indicate a missing `follows` directive in one of your flake inputs.

Example of duplicate entries in `flake.lock`:

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
}
```

To locate the source of duplicate entries, grep your `flake.lock` file. For example, if `home-manager` is referencing `nixpkgs_2` instead of the main `nixpkgs`:

```json
"home-manager": {
  "inputs": {
    "nixpkgs": "nixpkgs_2"
  }
}
```

Fix this by adding the following line to your `flake.nix` inputs:

```nix
home-manager.inputs.nixpkgs.follows = "nixpkgs";
```

Repeat this process until all duplicate `nixpkgs` entries are resolved. This ensures all inputs use the same `nixpkgs` source, preventing cross-version conflicts.
