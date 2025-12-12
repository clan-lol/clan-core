!!! Danger "Experimental"
    This service is experimental and will change in the future.

---

This module sets up [yggdrasil](https://yggdrasil-network.github.io/) across your clan.

Yggdrasil is designed to be a future-proof and decentralised alternative to the
structured routing protocols commonly used today on the internet. Inside your
clan, it will allow you to reach all of your machines.

If you have other services in your inventory which export peers (e.g. the
`internet` or the VPN services) as [service
exports](https://docs.clan.lol/reference/options/clan_service/#exports), they
will be added as yggdrasil peers automatically. This allows using the stable
yggdrasil IPv6 address to refer to other hosts and letting yggdrasil decide on
the best routing based on available connections.

The yggdrasil IPv6-address will be added to `/etc/hosts` using the
[meta.domain](https://docs.clan.lol/reference/options/clan/#meta.domain)
settings, allowing you to reach each host in the clan via
`<hostname>.<meta.domain>`.

Yggdrasil also does auto-discovery of local peers per default.

## Basic Usage Example

The simplest set-up is deploying yggdrasil on its own:

```nix
inventory = {

  machines = {
    peer1 = { };
    peer2 = { };
  };

  instances = {
    # Deploy yggdraisl on all machines
    yggdrasil = {
      roles.default.tags.all = { };
    };
  };
};
```

## Complex Usage Example

This example demonstrates a more sophisticated setup that combines yggdrasil
with multiple network clan services. By setting `meta.domain = "ccc"`, you can
access any machine in your clan using `<hostname>.ccc` (e.g., `peer1.ccc` or
`peer2.ccc`). Yggdrasil will automatically choose the best available routing
path between machines, whether that's via direct internet connection (`internet`
service_, the
mycelium mesh network, or through Tor hidden services. This provides resilient
connectivity with automatic failover between different network transports.

```nix
inventory = {

  machines = {
    peer1 = { };
    peer2 = { };
  };

  meta.domain = "ccc";

  instances = {

    # Deploy yggdraisl on all machines
    yggdrasil = {
      roles.default.tags.all = [ "all" ];
    };

    internet = {
      roles.default.machines = {
        peer1.settings.host = "85.139.10.1";
        peer2.settings.host = "85.139.10.2";
      };
    };

    mycelium = {
      roles.peer.tags.all = { };
    };

    tor = {

      roles.client.tags = [ "all" ];
      roles.server.tags = [ "all" ];

      roles.server.settings = {
        
        secretHostname = false;

        # yggdrasil ports need to be mapped
        portMapping = [
          {
            port = 6443;
            target.port = 6443;
          }
          {
            port = 6446;
            target.port = 6446;
          }
        ];
      };
    };
  };
};
```

## Security: Automatic Whitelisting

The Yggdrasil service implements **two layers of security** to restrict connections
to only clan members:

### Layer 1: Peer Whitelisting (Application Level)
Uses Yggdrasil's `AllowedEncryptionPublicKeys` to control which nodes can establish
peering connections:
- **Automatic**: All machines in the `default` role are automatically whitelisted
- **Isolation**: Public nodes cannot peer with your Yggdrasil instance
- **Multicast**: Local discovery via multicast is still enabled by default

### Layer 2: Firewall Rules (Network Level)
Restricts the `ygg` network interface to only accept traffic from clan member IPs:
- **IP-based filtering**: Only allows IPv6 traffic from known clan Yggdrasil addresses
- **Interface-specific**: Rules only apply to the `ygg` interface
- **Defense in depth**: Blocks traffic even if a non-clan node somehow peers
- **Automatic**: Works with both nftables and iptables backends

**Combined Effect**: Only clan members can both peer AND route traffic through
your Yggdrasil instance, providing comprehensive protection against unauthorized access.
