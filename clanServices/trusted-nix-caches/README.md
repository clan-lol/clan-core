Sets up nix to trust and use the clan cache

## Usage

```nix
inventory.instances = {
  clan-cache = {
    module = {
      name = "trusted-nix-caches";
      input = "clan";
    };
    roles.default.machines.draper = { };
  };
}
```
