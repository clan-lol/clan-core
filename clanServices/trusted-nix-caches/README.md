Sets up Nix to trust and use the Clan cache

## Usage

```nix
inventory.instances = {
  clan-cache = {
    module = {
      name = "trusted-nix-caches";
      input = "clan-core";
    };
    roles.default.machines.draper = { };
  };
}
```
