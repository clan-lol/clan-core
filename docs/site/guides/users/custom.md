# Custom

## Custom User Management

The [users service](/docs/services/official/users) handles most cases. This guide covers alternative approaches for when you need more control.

### Manual NixOS Users

Define users directly in your machine configuration when you need full control over user settings or want to avoid the users service abstraction.

```nix [machines/jon/default.nix]
{ config, ... }:
{
  users.users.alice = {
    isNormalUser = true;
    home = "/home/alice";
    extraGroups = [
      "wheel"
      "networkmanager"
    ];
    # Password set via hashedPassword or initialPassword
    # Or use clan's vars system for secrets
  };
}
```

This approach works well when:

- You have machine-specific user configurations
- You want to use NixOS user options directly
- You're migrating from an existing NixOS setup

### Shared User Modules

If the same user needs access to multiple machines, define them in a shared module:

```
.
├── machines/
│   ├── desktop/
│   │   └── default.nix
│   └── laptop/
│       └── default.nix
└── users/
    └── alice/
        └── default.nix
```

```nix [users/alice/default.nix]
{ ... }:
{
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [
      "wheel"
      "networkmanager"
      "video"
    ];
  };
}
```

Then import it in each machine:

```nix [machines/desktop/default.nix]
{ ... }:
{
  imports = [ ../../users/alice ];
}
```

### Integrating home-manager

[home-manager](https://github.com/nix-community/home-manager) manages user-specific dotfiles and packages. You can integrate it with Clan's users service via `extraModules`.

First, add home-manager to your flake inputs:

```nix [flake.nix]
{
  inputs = {
    # ... existing inputs
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };
}
```

Then use `extraModules` to attach home-manager configuration to a user:

```nix [clan.nix] {10}
{
  inventory.instances = {
    alice-user = {
      module.name = "users";
      roles.default.tags.all = { };
      roles.default.settings = {
        user = "alice";
        groups = [
          "wheel"
          "networkmanager"
        ];
      };
      roles.default.extraModules = [ ./users/alice/home.nix ];
    };
  };
}
```

```nix [users/alice/home.nix]
{ self, ... }:
{
  imports = [ self.inputs.home-manager.nixosModules.default ];

  home-manager.users.alice = {
    home.stateVersion = "24.05";

    programs.git = {
      enable = true;
      userName = "Alice";
      userEmail = "alice@example.com";
    };

    # Add more home-manager configuration here
  };
}
```

The `extraModules` option accepts paths to NixOS modules. These modules are added to every machine that has this user.
