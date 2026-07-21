# Mycelium Networking

[Mycelium](https://github.com/threefoldtech/mycelium) is an end-to-end encrypted IPv6 overlay network. Every machine generates a private key, and its IPv6 address is derived from that key, making the address stable and globally unique. Machines find each other through a combination of public bootstrap nodes and locality-aware routing that picks the shortest available path.

Mycelium has a priority of 800, placing it below WireGuard (1000) and above Tor (10).

## When to Use

Mycelium is a good choice when:

- You want a zero-configuration mesh with no controller role to assign
- Your machines are behind NAT and you don't have a server with a public endpoint to act as a WireGuard controller
- You want locality-aware routing that adapts to physical network topology
- You want a fallback between WireGuard and Tor in a layered networking setup

Unlike WireGuard, Mycelium has no controller requirement: machines join the global Mycelium network through public nodes maintained by the Mycelium project and discover each other from there. You don't need to manage any infrastructure.

## Roles

Mycelium has a single role: `peer`. Every machine in your inventory that you want on the Mycelium network gets this role. You can read about [Mycelium's roles here](/docs/services/official/mycelium#roles).

## Basic Example

```nix
# clan.nix
inventory.instances = {
  mycelium = {
    roles.peer.tags = [ "all" ];
  };
};
```

That's the entire configuration. After running `clan vars generate` and deploying, every machine has a stable IPv6 address derived from its private key and can reach every other machine on the network.

## Complete Example

Here Mycelium provides a mesh between all machines, with the `internet` service for direct SSH access to servers that have public addresses and Tor as a final fallback:

```nix
# clan.nix
inventory.machines = {
  web-server   = { tags = [ "server" ]; };
  db-server    = { tags = [ "server" ]; };
  sally-laptop = { tags = [ "laptop" ]; };
  fred-laptop  = { tags = [ "laptop" ]; };
};

inventory.instances = {
  # Direct SSH for machines with public addresses
  internet = {
    roles.default.machines."web-server".settings.host = "web.example.com";
    roles.default.machines."db-server".settings.host  = "db.example.com";
  };

  # Mycelium mesh across all machines
  mycelium = {
    roles.peer.tags = [ "all" ];
  };

  # Tor as last-resort fallback
  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

Clan tries direct SSH first (priority 2000), then Mycelium (priority 800), then Tor (priority 10). The laptops, which have no public addresses, are always reachable via Mycelium.
