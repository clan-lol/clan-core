# How it works

Clan needs to know how to reach your machines when you run commands like `clan machines update` or `clan ssh`. To do so, you declare a **networking service** that tells Clan how to connect to each machine.

The real advantage is that you can configure more than one networking service at a time. Clan tries them in priority order until one succeeds. If your direct connection fails, it falls back to your VPN. If the VPN is down, it falls back to Tor. You don't have to decide which path to use; Clan works through them automatically.

## Available Networking Services

Here are the services in order from highest (first) to lowest (last).

| Service | Priority | What It Does |
|---------|----------|--------------|
| `p2p-ssh-iroh` | 3000 | Peer-to-peer SSH via Iroh |
| `internet` | 2000 | Direct SSH via IP address or hostname |
| `wireguard` | 1000 | WireGuard VPN mesh with auto-assigned IPs |
| `zerotier` | 900 | ZeroTier VPN mesh with auto-assigned IPs |
| `mycelium` | 800 | Mycelium peer-to-peer overlay network |
| `tor` | 10 | Tor onion services; lowest priority, last-resort fallback |

A higher priority number means Clan tries that service first. When multiple services are configured, Clan works down the list from highest to lowest until it finds one that works.

## P2P SSH (Iroh): NAT-Traversing SSH

:::admonition[Experimental]{type=danger}
This service is experimental and will change in the future.
:::

The `p2p-ssh-iroh` service enables SSH access to machines behind NAT or firewalls without port forwarding. It uses [Iroh](https://github.com/n0-computer/dumbpipe)'s peer-to-peer networking to establish encrypted QUIC streams, falling back to relay servers when a direct connection cannot be established.

This is the highest-priority networking service (3000), meaning Clan tries it first. Because it handles NAT traversal automatically, `clan ssh <machine>` works from any admin machine, even one that isn't inside the clan's VPN or on the same network.

The `server` role exposes a machine's SSH service via Iroh. There is no client role; any machine running Clan can connect to a server.

```nix
# clan.nix
inventory.instances = {
  p2p-ssh-iroh = {
    roles.server.tags = [ "all" ];
  };
};
```

:::admonition[Security Notice]{type=warning}
Enabling this service exposes the machine's SSH service to anyone on the Iroh network. The only protection against unauthorized access is SSH authentication itself. Make sure all machines have SSH access configured securely. Use private key authentication only and disable password login.
:::

## Internet: Direct SSH

The `internet` service is the simplest option. You give each machine a hostname or IP address and Clan connects directly via SSH.

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."my-server".settings.host = "server.example.com";
    roles.default.machines."my-laptop".settings.host = "192.168.1.10";
  };
};
```

By default, Clan connects as `root` on port 22. You can override both per machine:

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."my-server" = {
      settings.host = "server.example.com";
      settings.user = "admin";
      settings.port = 2222;
    };
  };
};
```

## WireGuard: VPN Mesh

WireGuard creates a secure mesh network between your machines using automatic IPv6 address allocation. It assigns addresses automatically. You don't need to manage them yourself.

The WireGuard service has two roles, controller and peer; you can [read more about them here](/docs/services/official/wireguard#roles).

All traffic between peers flows through controllers, which have IPv6 forwarding enabled. Controllers also connect to each other in a full mesh.

```nix
# clan.nix
inventory.instances = {
  wireguard = {
    roles.controller.machines."my-server" = {
      settings.endpoint = "vpn.example.com";
    };
    roles.peer.tags = [ "all" ];
  };
};
```

The controller must have a publicly accessible endpoint. By default, WireGuard uses UDP port 51820, which you can change with `settings.port`.

Machines in the network are automatically added to `/etc/hosts` and can be reached by hostname in the format `<machine-name>.<instance-name>` (for example, `server1.wireguard`).

## ZeroTier: Mesh VPN

ZeroTier creates a private mesh network between your machines. Each machine gets an automatically assigned IP address; you don't need to know or track the addresses yourself. Clan generates and stores them.

The ZeroTier service requires exactly one machine to act as the **controller**. The controller manages network membership and admits machines to the network. All other machines are **peers**.

```nix
# clan.nix
inventory.instances = {
  zerotier = {
    # In this example, we are declaring my-server as the controller
    roles.controller.machines."my-server" = {};
    roles.peer.tags = [ "all" ];
  };
};
```

Here `my-server` is the controller. Every machine in the inventory (via the `all` tag) joins as a peer. The controller is included in the `all` tag and participates as a peer as well.

The controller must be reachable by all peers, so it should be a machine with a stable public address. Pairing the `internet` service with ZeroTier is a good way to ensure the controller is always reachable while the peers connect via the mesh.

### Moon Nodes

If peers can't reach the controller directly (behind NAT, for example, or under an offline VPN in fully sandboxed environments), you can designate one or more machines as **moon** relay nodes. A moon must have a stable public address. Machines will connect to the network through one of these relay nodes.

```nix
# clan.nix
inventory.instances = {
  zerotier = {
    roles.controller.machines."my-server" = {};
    roles.moon.machines."relay-server" = {
      settings.stableEndpoints = [ "203.0.113.5" ];
    };
    roles.peer.tags = [ "all" ];
  };
};
```

## Mycelium: P2P Overlay Network

[Mycelium](https://github.com/threefoldtech/mycelium) is an end-to-end encrypted IPv6 overlay network. It features locality-aware routing (finding the shortest path between nodes), automatic rerouting if a link goes down, and IPv6 addresses derived from private keys. It supports multiple transports (QUIC, TCP) and is designed for planetary-scale scalability.

The configuration is minimal; there is only a `peer` role:

```nix
# clan.nix
inventory.instances = {
  mycelium = {
    roles.peer.tags = [ "all" ];
  };
};
```

This connects all your machines to the Mycelium network. No controller or special infrastructure is needed.

## Tor: Onion Service Fallback

Tor gives every machine a `.onion` address, making it reachable even without a public IP or open ports. Because Tor has the lowest priority (10), Clan only uses it when every other configured networking service has failed. It is meant as a last-resort fallback.

The `server` role sets up the onion service on machines you want to reach. The `client` role enables a persistent Tor proxy on machines that need to connect. If you don't assign the `client` role, Clan starts a temporary Tor proxy automatically when needed, so it is optional.

```nix
# clan.nix
inventory.instances = {
  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

With just this, every machine gets a Tor onion address. Clan generates the onion keys automatically via `clan vars generate`.

To keep a Tor proxy running persistently on a machine that frequently initiates connections:

```nix
# clan.nix
inventory.instances = {
  tor = {
    roles.server.tags = [ "all" ];
    roles.client.machines."my-laptop" = {};
  };
};
```

## Combining Services

The real power of the networking system shows when you use multiple services together. Clan tries the highest-priority service first and falls back automatically if it cannot connect.

A straightforward setup: direct SSH for a public server, with Tor as a universal fallback for everything:

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."my-server".settings.host = "server.example.com";
  };

  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

In this example, Clan always tries direct SSH first through the Internet service. If that fails, it falls back to Tor (priority 10).

Here's an example that includes a mesh setup with Tor as the final fallback:

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."my-server".settings.host = "server.example.com";
  };

  zerotier = {
    roles.controller.machines."my-server" = {};
    roles.peer.tags = [ "all" ];
  };

  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

Clan tries direct SSH first through the Internet service, then ZeroTier, then Tor.

## Emergency Override

If all configured networking is failing and you need to reach a machine directly, you can bypass the networking system entirely with the `--target-host` flag:

```bash
clan machines update my-server --target-host root@backup-ip.example.com
clan ssh my-server --target-host root@10.0.0.5
```

This is intended for debugging and emergency access only.
