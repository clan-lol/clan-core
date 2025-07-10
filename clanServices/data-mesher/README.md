This service will set up data-mesher.

## Usage

```nix
inventory.instances = {
  data-mesher = {
    module = {
      name = "data-mesher";
      input = "clan-core";
    };
    roles.admin.machines.server0 = {
      settings = {
        bootstrapNodes = {
          node1 = "192.168.1.1:7946";
          node2 = "192.168.1.2:7946";
        };

        network = {
          hostTTL = "24h";
          interface = "tailscale0";
        };
      };
    };
    roles.peer.machines.server1 = { };
    roles.signer.machines.server2 = { };
  };
}
```
