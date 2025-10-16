This module sets up [yggdrasil](https://yggdrasil-network.github.io/) across your clan. 

Yggdrasil is designed to be a future-proof and decentralised alternative to
the structured routing protocols commonly used today on the internet. Inside your clan, it will allow you to reach all of your machines.

## Example Usage

While you can specify statically configured peers for each host, yggdrasil does auto-discovery of local peers.

```nix
inventory = {

  machines = {
    peer1 = { };
    peer2 = { };
  };

  instances = {
    yggdrasil = {

      # Deploy on all machines
      roles.default.tags.all = { };

      # Or individual hosts
      roles.default.machines.peer1 = { };
      roles.default.machines.peer2 = { };
    };
  };
};
```
