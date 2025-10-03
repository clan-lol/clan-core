!!! Note "Under construction"

The users concept of clan is not done yet. This guide outlines some solutions from our community.
Defining users can be done in many different ways. We want to highlight two approaches:

- Using clan's [users](../../reference/clanServices/users.md) service.
- Using a custom approach.

## Adding Users using the [users](../../reference/clanServices/users.md) service

To add a first *user* this guide will be leveraging two things:

- [clanServices](../../reference/clanServices/index.md): Allows to bind arbitrary logic to something we call an `ìnstance`.
- [clanServices/users](../../reference/clanServices/users.md): Implements logic for adding a single user perInstance.

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
        # ...
        # elided
    };
}
```

1. Add `user = jon` as a user on all machines. Will create a `home` directory, and prompt for a password before deployment.
2. Add this user to `all` machines
3. Define the `name` of the user to be `jon`

The `users` service creates a `/home/jon` directory, allows `jon` to sign in and will take care of the user's password.

For more information see [clanService/users](../../reference/clanServices/users.md)

## Using a custom approach

Some people like to define a `users` folder in their repository root.
That allows to bind all user specific logic to a single place (`default.nix`)
Which can be imported into individual machines to make the user available on that machine.

```bash
.
├── machines
│   ├── jon
# ......
├── users
│   ├── jon
│   │   └── default.nix # <- a NixOS module; sets some options
# ... ... ...
```

## using [home-manager](https://github.com/nix-community/home-manager)

When using clan's `users` service it is possible to define extraModules.
In fact this is always possible when using clan's services.

We can use this property of clan services to bind a nixosModule to the user, which configures home-manager.

```{.nix title="clan.nix" hl_lines="22"}
{
    inventory.machines = {
        jon = { };
        sara = { };
    };
    inventory.instances = {
        jon-user = {
            module.name = "users";

            roles.default.tags.all = { };

            roles.default.settings = {
                user = "jon",
                groups = [
                    "wheel"
                    "networkmanager"
                    "video"
                    "input"
                ];
            };

            roles.default.extraModules = [ ./users/jon/home.nix ]; # (1)
        };
        # ...
        # elided
    };
}
```

1. Type `path` or `string`: Must point to a separate file. Inlining a module is not possible

!!! Note "This is inspiration"
    Our community might come up with better solutions soon.
    We are seeking contributions to improve this pattern if you have a nicer solution in mind.

```nix title="users/jon/home.nix"
# NixOS module to import home-manager and the home-manager configuration of 'jon'
{ self, ...}:
{
  imports = [ self.inputs.home-manager.nixosModules.default ];
  home-manager.users.jon = {
    imports = [
      ./home-configuration.nix
    ];
  };
}
```
