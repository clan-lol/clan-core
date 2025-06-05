LocalSend is a free, open-source alternative to AirDrop that allows you to
securely share files and messages with nearby devices over your local network
without needing an internet connection.

## Example Usage

```nix
inventory.instances = {
  localsend = {
    module = {
      name = "localsend";
      input = "clan";
    };
    roles.default.machines.draper = { };
  };
}
```
