This service will automatically set the emergency access password if your system fails to boot.

## Usage

```nix
inventory.instances = {
  mylounge = {
    module = {
      name = "emergency-access";
      input = "clan-core";
    };

    roles.default.tags.nixos = { };
  };
}
```
