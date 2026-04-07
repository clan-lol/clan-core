## Usage

```nix
{
  inventory.instances = {
    # Deploy user alice on all machines. Don't prompt for password (will be
    # auto-generated).
    user-alice = {
      module = {
        name = "users";
        input = "clan-core";
      };
      roles.default.tags = [ "all" ];
      roles.default.settings = {
        user = "alice";
        prompt = false;
      };
    };

    # Deploy user Carol on all machines. Prompt only once and use the
    # same password on all machines. (`share = true`)
    user-carol = {
      module = {
        name = "users";
        input = "clan-core";
      };
      roles.default.tags = [ "all" ];
      roles.default.settings = {
        user = "carol";
        share = true;
        openssh.authorizedKeys.keys = [
          "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ..."
        ];
      };
    };

    # Deploy user bob only on his laptop. Prompt for a password.
    user-bob = {
      module = {
        name = "users";
        input = "clan-core";
      };
      roles.default.machines.bobs-laptop = { };
      roles.default.settings.user = "bob";
    };
  };
}
```

## Integrating home-manager

[home-manager](https://github.com/nix-community/home-manager) manages user-specific dotfiles and packages. You can integrate it with the users service via `extraModules`.

First, add home-manager to your flake inputs:

```nix
{
  inputs = {
    # ... existing inputs
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };
}
```

Then use `extraModules` to attach home-manager configuration to a user:

```nix
{
  inventory.instances = {
    alice-user = {
      module.name = "users";
      roles.default.tags = [ "all" ];
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

```nix
# users/alice/home.nix
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

## Migration from `root-password` module

The deprecated `clan.root-password` module has been replaced by the `users` module. Here's how to migrate:

### 1. Update your flake configuration

Replace the `root-password` module import with a `users` service instance:

```nix
# OLD - Remove this from your nixosModules:
imports = [
  self.inputs.clan-core.clanModules.root-password
];

# NEW - Add to inventory.instances or machines/flake-module.nix:
instances = {
  users-root = {
    module.name = "users";
    module.input = "clan-core";
    roles.default.tags = [ "nixos" ];
    roles.default.settings = {
      user = "root";
      prompt = false;  # Set to true if you want to be prompted
      groups = [ ];
    };
  };
};
```

### 2. Migrate vars

The vars structure has changed from `root-password` to `user-password-root`:

```bash
# For each machine, rename the vars directories:
cd vars/per-machine/<machine-name>/
mv root-password user-password-root
mv user-password-root/password-hash user-password-root/user-password-hash
mv user-password-root/password user-password-root/user-password
```
