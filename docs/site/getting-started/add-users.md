## Summary

You will create a user that can log in to machines.

## Requirements

- A working Clan setup with at least one machine

## Adding Users

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

What happens here:

- [services/users](../services/official/users.md): Implements logic for adding a single user.

The `users` service:

- creates a `/home/jon` directory.
- allows `jon` to sign in.
- takes care of the user's password.

For more information see [services/users](../services/official/users.md)

## Checkpoint

To verify your user configuration is correct, run:

```bash
clan vars generate $MACHINE_NAME
```

If the command completes without errors and prompts you to set a password for your user, the configuration is working correctly.

## Up Next

In the next step, we will add a few recommended services to your Clan setup.
