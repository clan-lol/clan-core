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
