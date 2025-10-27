🚧🚧🚧 Experimental 🚧🚧🚧

Use at your own risk.

We are still refining its interfaces, instability and breakages are expected.

---

This module sets up [yggdrasil](https://yggdrasil-network.github.io/) across your clan. 

Yggdrasil is designed to be a future-proof and decentralised alternative to the
structured routing protocols commonly used today on the internet. Inside your
clan, it will allow you to reach all of your machines.

If you have other services in your inventory which export peers (e.g. the
`internet` or the services) as [service
exports](https://docs.clan.lol/reference/options/clan_service/#exports), they
will be added as yggdrasil peers automatically. This allows using the stable
yggdrasil IPv6 address to refer to other hosts and letting yggdrasil decide on
the best routing based on available connections.

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
