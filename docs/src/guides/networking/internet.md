# Internet Networking

The `internet` service tries to keep connections straightforward by letting you give each machine a hostname or IP address. Clan can then connect directly via SSH. Use it when your machines have stable, reachable addresses: public IPs, DNS hostnames, or local network addresses that don't change.

When Clan connects to a machine, it tries networking services in priority order. The `internet` service has a priority of 2000, the second highest of the networking services, behind only `p2p-ssh-iroh`. That means if you don't have the `p2p-ssh-iroh` service, Clan always tries to use the Internet service's direct SSH first. If the connection fails and you have other networking services configured, Clan falls back to them automatically.

:::admonition[Experimental]{type=danger}
This service is experimental and might change in the future.
:::

## When to Use

Use the `internet` service when:

* Your machines have public IP addresses or DNS hostnames
* Your machines are on a local network and always reachable by IP
* You want the simplest possible networking setup with no VPN infrastructure
* You want direct SSH as the first-choice connection method, with other services as fallback

If your machines are behind NAT and have no way to be reached directly, the `internet` service won't work on its own. Consider adding ZeroTier or Tor alongside it, or instead of it.

## Roles

The `internet` service has a single role, `default`. You can read more about [Internet's roles here](/docs/services/official/internet#roles).

## Guides

For a complete guide that uses the Internet service, see any of these Getting Started Guides:

* [Getting Started: Physical Machine Target](../../getting-started/getting-started-physical)
* [Getting Started: Hetzner Edition](../../getting-started/getting-started-hetzner)
* [Getting Started: AWS Edition](../../getting-started/getting-started-aws)
* [Getting Started: Google Cloud Edition](../../getting-started/getting-started-google)
* [Getting Started: VirtualBox Edition](../../getting-started/getting-started-virtualbox)

## Basic Example

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."web-server".settings.host  = "web.example.com";
    roles.default.machines."backup-server".settings.host = "192.168.1.100";
  };
};
```

Both machines use the defaults: connect as `root` on port 22.

## Another Example

This example shows a setup with machines that need different settings: a standard server, one with a non-standard port and user, and one that is only reachable through a jump host.

```nix
# clan.nix
{
  inventory.machines = {
    web-server = {
      tags = [ "server" ];
    };
    db-server = {
      tags = [ "server" ];
    };
    admin-box = {
      tags = [ "server" ];
    };
  };

  inventory.instances = {
    internet = {
      # Public web server, standard SSH defaults
      roles.default.machines."web-server" = {
        settings.host = "web.example.com";
      };

      # Database server on a non-standard port with a dedicated deploy user
      roles.default.machines."db-server" = {
        settings.host = "db.example.com";
        settings.port = 2222;
        settings.user = "deploy";
      };

      # Admin box behind a firewall, reachable only through a jump host
      roles.default.machines."admin-box" = {
        settings.host = "admin.internal.example.com";
        settings.jumphosts = [ "jump.example.com" ];
      };
    };
  };
}
```

When Clan connects to `admin-box`, it tunnels through `jump.example.com` automatically.

## Using Internet with Other Networking Services

Because `internet` has the second highest priority behind only p2p-ssh-iroh, it works well as your first-choice connection method with other services providing fallback. A common pattern is direct SSH through the Internet service for machines with known addresses, plus ZeroTier for machines that may move between networks:

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."web-server".settings.host    = "web.example.com";
    roles.default.machines."backup-server".settings.host = "backup.example.com";
  };

  zerotier = {
    roles.controller.machines."web-server" = {};
    roles.peer.tags = [ "all" ];
  };
};
```

Assuming you've maintained the default priorities, Clan tries direct SSH through the Internet service first. If a machine is temporarily unreachable at its public address (for example, a laptop that has moved to a different network) Clan falls back to ZeroTier, which can reach it through the mesh regardless of its physical location.
