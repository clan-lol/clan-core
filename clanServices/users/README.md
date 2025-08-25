## Usage

```nix
{
  inventory.instances = {
    # Deploy user alice on all machines. Don't prompt for password (will be
    # auto-generated).
    user-alice = {
      module = {
        name = "users";
        input = "clan";
      };
      roles.default.tags.all = { };
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
        input = "clan";
      };
      roles.default.tags.all = { };
      roles.default.settings = {
        user = "carol";
        share = true;
      };
    };

    # Deploy user bob only on his laptop. Prompt for a password.
    user-bob = {
      module = {
        name = "users";
        input = "clan";
      };
      roles.default.machines.bobs-laptop = { };
      roles.default.settings.user = "bob";
    };
  };
}
```

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
    roles.default.tags.nixos = { };
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
