## Summary

Create user accounts that can log in to your machines. In this example every user can access every machine, but per-machine access is also possible.

This guide uses Clan's [users](../services/official/users.md) service.

## Requirements

- Estimated time: 30min
- A working Clan setup with at least one machine

## Adding Users

To add a first *user* this guide will be leveraging two things:

- [services](../services/definition.md): Allows binding arbitrary logic to an `instance`.
- [services/users](../services/official/users.md): Implements logic for adding a single user.

The example shows how to add a user called `jon`:

```{.nix title="clan.nix" hl_lines="7-21"}
{
  inventory.machines = {
      jon = { };
      sara = { };
  };
  inventory.instances = {
    jon-user = { # (1)
      module.name = "users";
      roles.default.tags.all = { }; # (2)
      roles.default.settings = {
        user = "jon"; # (3)
        groups = [
          "wheel" # Allow using 'sudo'
          "networkmanager" # Allows to manage network connections.
          "video" # Allows to access video devices.
          "input" # Allows to access input devices.
        ];
      };
    };
  };
}
```

1. Add `user = jon` as a user on all machines. Will create a `home` directory, and prompt for a password before deployment.
2. Add this user to `all` machines
3. Define the `name` of the user to be `jon`

The `users` service:

- creates a `/home/jon` directory.
- allows `jon` to sign in.
- takes care of the user's password.

For more information see [services/users](../services/official/users.md)

## Checkpoint

To verify your user configuration is correct, run:

```bash
clan machines update $MACHINE_NAME --dry-run
```

If the command completes without errors and prompts you to set a password for your user, the configuration is working correctly.


## Up Next

In the next step, we will add a few recommended services to your Clan setup.
