# WireGuard Networking

WireGuard creates a private, encrypted VPN mesh between your machines using automatic IPv6 address allocation. Every machine gets a stable address on the network without manual configuration, and keys are generated and distributed by Clan through the vars system.

WireGuard has a priority of 1000, so if you also configure the `internet` service (priority 2000), Clan tries direct SSH first and falls back to WireGuard if that fails.

## How It Differs from ZeroTier

Both WireGuard and ZeroTier create encrypted private networks with auto-assigned IPs, but they work differently:

- **ZeroTier** attempts direct peer-to-peer connections and routes through relay nodes only when needed. The controller just manages membership; peers talk to each other directly when possible.
- **WireGuard** routes all peer traffic through controllers. Controllers must have publicly reachable endpoints. Peers never talk to each other directly; traffic always hops through a controller.

Use WireGuard when you want the performance and simplicity of a well-established VPN protocol and you have at least one server with a public address to act as a controller. Use ZeroTier when you want true P2P connectivity and are comfortable with its additional complexity.

## Requirements

- Controllers must have a stable, publicly reachable endpoint (IP address or DNS hostname)
- Peers must be in networks where UDP traffic is not blocked (WireGuard uses port 51820 by default)

## Roles

Wireguard has two roles, `controller` and `peer`. You can read more about [Wireguard's roles here](/docs/services/official/wireguard#roles).

## Basic Example

```nix
# clan.nix
inventory.machines = {
  vpn-server   = { tags = [ "server" ]; };
  sally-laptop = { tags = [ "laptop" ]; };
  fred-laptop  = { tags = [ "laptop" ]; };
};

inventory.instances = {
  wireguard = {
    roles.controller.machines."vpn-server" = {
      settings.endpoint = "vpn.example.com";
    };
    roles.peer.tags = [ "laptop" ];
  };
};
```

`vpn-server` is the controller. The laptops are peers and connect to it. Note that the `laptop` tag is used for peers rather than `all`: a machine cannot be both a controller and a peer in the same WireGuard instance, so you must keep the controller out of the peer role.

## Guide

This guide walks you through trying out WireGuard.

To try out the WireGuard feature, create two cloud servers using the initial part of the Getting Started guide for a cloud (such as [AWS](../../getting-started/getting-started-aws) or [Hetzner](../../getting-started/getting-started-hetzner)), including adding your id_ed25519 key pair.

:::admonition[Important]{type=important}
Your controller node requires a permanent, static public IP address to maintain consistent mesh connectivity. (The peer machines do not need static IPs; they can safely rely on dynamic addresses assigned at startup, even if those IPs change across reboots. If a peer's IP address does change, simply update that machine's settings.host entry under the internet section of your clan.nix file. )
:::

:::admonition[Important]{type=important}
Enable incoming UDP Port 51820 for both servers.
:::

Create the clan, calling it CLAN-WG:

```bash
nix run https://clan.lol/install/{{ version }} --refresh -- init
cd CLAN-WG
direnv allow
```

and then create the two machines:

```bash
clan machines create my-controller
clan machines create peer1
```

:::admonition[Important]{type=important}
If you're practicing, you need to create at least one controller and one peer; otherwise, with only one machine, you'll get an error when you try to perform a `machines update`.
:::

Here's a clan.nix file that supports the two machines:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "CLAN-WG";
  meta.domain = "clanwg.lol";

  inventory.machines = {
    controller = {
      tags = [
        "controller"
        "all"
      ]; # todo - rename to my-controller
    };
    peer1 = {
      tags = [
        "peers"
        "all"
      ];
    };

  };

  inventory.instances = {

    wireguard = {
      roles.controller.machines."my-controller" = {
        # todo - rename to my-controller
        settings.endpoint = "<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S CONTROLLER IP ADDRESS
        settings.port = 51820;
      };
      roles.peer.machines."peer1" = {
        settings.controller = "my-controller";
      };
    };

    internet = {
      roles.default.machines."my-controller" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S CONTROLLER IP ADDRESS
        settings.user = "root";
      };
      roles.default.machines."peer1" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S PEER IP ADDRESS
        settings.user = "root";
      };

    };

    # Docs: https://clan.lol/docs/services/official/sshd
    # SSH service for secure remote access to machines.
    # Generates persistent host keys and configures authorized keys.
    sshd = {
      roles.server.tags.all = { };
      roles.server.settings.authorizedKeys = {
        # Insert the public key that you want to use for SSH access.
        # All keys will have ssh access to all machines ("tags.all" means 'all machines').
        # Alternatively set 'users.users.root.openssh.authorizedKeys.keys' in each machine
        "admin-machine-1" = "PASTE_YOUR_KEY_HERE";
      };
    };

    # Docs: https://clan.lol/docs/unstable/services/official/users
    # Root password management for all machines.
    user-root = {
      module = {
        name = "users";
      };
      roles.default.tags.all = { };
      roles.default.settings = {
        user = "root";
        prompt = true;
      };
    };
  };
}
```

Update the IP addresses in the `clan.nix` file where noted, and add in your authorized key.

Gather the hardware configurations:

```bash
clan machines init-hardware-config my-controller
clan machines init-hardware-config peer1
```

(For AWS, you'll add on `--target-host ubuntu@<IP-ADDRESS>` to each line.)

Add a disk configuration using the usual approach of re-running each command with the generated output added inside double-quotes:

```bash
clan templates apply disk ext4-single-disk my-controller --set mainDisk ""
clan templates apply disk ext4-single-disk peer1 --set mainDisk ""
```

Install the controller, and then the peer:

```bash
clan machines install controller
clan machines install peer1
```

or, if you already installed and are just adding WireGuard, simply update:

```bash
clan machines update
```

Now you're ready to test. One way to test out the WireGuard network is by connecting to each server by SSH and try connecting to the other using the name of the other server. Here we first connect SSH into the controller and try pinging the peer. Notice the name has a `.wireguard` added onto it:

```bash
[root@controller:~]# ping peer1.wireguard
PING peer1.wireguard (fd28:387a:c1:4700:6987:50a0:9b93:4337) 56 data bytes
64 bytes from peer1.wireguard (fd28:387a:c1:4700:6987:50a0:9b93:4337): icmp_seq=1 ttl=64 time=0.928 ms
64 bytes from peer1.wireguard (fd28:387a:c1:4700:6987:50a0:9b93:4337): icmp_seq=2 ttl=64 time=1.08 ms
64 bytes from peer1.wireguard (fd28:387a:c1:4700:6987:50a0:9b93:4337): icmp_seq=3 ttl=64 time=0.975 ms
64 bytes from peer1.wireguard (fd28:387a:c1:4700:6987:50a0:9b93:4337): icmp_seq=4 ttl=64 time=0.991 ms
^C
```

Now we SSH into the peer and try the reverse:

```bash
[root@peer1:~]# ping controller.wireguard
PING controller.wireguard (fd28:387a:c1:4700::1) 56 data bytes
64 bytes from controller.wireguard (fd28:387a:c1:4700::1): icmp_seq=1 ttl=64 time=0.991 ms
64 bytes from controller.wireguard (fd28:387a:c1:4700::1): icmp_seq=2 ttl=64 time=0.959 ms
64 bytes from controller.wireguard (fd28:387a:c1:4700::1): icmp_seq=3 ttl=64 time=1.00 ms
64 bytes from controller.wireguard (fd28:387a:c1:4700::1): icmp_seq=4 ttl=64 time=0.944 ms
^C
```

By shifting the network layer into a software-defined WireGuard mesh, Clan eliminates the operational overhead of managing complex cloud firewalls and routing tables.

Administrators only need to open a single generic port (UDP 51820) globally to establish a secure, encrypted transit path between nodes, while restricting SSH (Port 22) traffic exclusively to the IP address of the administrator's deployment machine for provisioning and updates.

Because WireGuard itself is cryptographically secure and completely silent to unauthorized traffic, internal infrastructure remains invisible to the public internet while allowing production services like databases, internal APIs, and peer-to-peer communications to run seamlessly over a unified private network layout.

## Hostname Resolution

WireGuard automatically adds entries to `/etc/hosts` for every machine in the network. Each machine is reachable using the format `<machine-name>.<instance-name>` with the instance named `wireguard` by default.

With the earlier code, for example, the `/etc/hosts` file looks like this on the peer:

```text
127.0.0.1 localhost
::1 localhost
127.0.0.2 peer1.clanwg.lol peer1
fd28:387a:c1:4700::1 controller.wireguard
fd28:387a:c1:4700:6987:50a0:9b93:4337 peer1.wireguard

```

:::admonition[Note]{type=info}
We've created an identity for loopback as well, using the domain name you provided when you first created the clan file: `peer1.clanwg.lol`. For example:

```bash
[root@peer1:~]# ping peer1.clanwg.lol
PING peer1.clanwg.lol (127.0.0.2) 56(84) bytes of data.
64 bytes from peer1.clanwg.lol (127.0.0.2): icmp_seq=1 ttl=64 time=0.038 ms
64 bytes from peer1.clanwg.lol (127.0.0.2): icmp_seq=2 ttl=64 time=0.041 ms
64 bytes from peer1.clanwg.lol (127.0.0.2): icmp_seq=3 ttl=64 time=0.053 ms
64 bytes from peer1.clanwg.lol (127.0.0.2): icmp_seq=4 ttl=64 time=0.052 ms
^C
```

:::

If you want a different suffix besides `wireguard`, set the `domain` option on the controller (peers inherit it). Try updating:

```nix
    wireguard = {
      roles.controller.machines."my-controller" = {
        settings.endpoint = "<IP-ADDRESS>";  # REPLACE WITH YOUR MACHINE'S CONTROLLER IP ADDRESS
        settings.port = 51820;
        settings.domain = "wg";
      };
      roles.peer.machines."peer1" = {
        settings.controller = "my-controller";
      };
    };
```

Then run the update:

```bash
clan machines update
```

Now after connected to either of the two servers, you can use `.wg` instead:

```bash
[root@controller:~]# ping peer1.wg
PING peer1.wg (fd28:387a:c1:4700:6987:50a0:9b93:4337) 56 data bytes
64 bytes from peer1.wg (fd28:387a:c1:4700:6987:50a0:9b93:4337): icmp_seq=1 ttl=64 time=0.922 ms
64 bytes from peer1.wg (fd28:387a:c1:4700:6987:50a0:9b93:4337): icmp_seq=2 ttl=64 time=0.996 ms
^C
```

## MTU Issues

If ping works but other connections behave strangely (dropped packets, stalled transfers), the WireGuard interface MTU may be too high for your network path. Try lowering it:

```nix
roles.controller.machines."vpn-server-1" = {
  settings.endpoint = "vpn1.example.com";
  settings.mtu = 1350;
};
```

Set the same MTU on peers if the controller alone doesn't resolve it. Start low (1280 is a safe minimum for IPv6) and work up to find the highest value that still works reliably.

## Pairing with Other Networking Services

WireGuard works well alongside the `internet` service for direct access to controllers, and Tor as a last-resort fallback:

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."vpn-server-1".settings.host = "vpn1.example.com";
    roles.default.machines."vpn-server-2".settings.host = "vpn2.example.com";
  };

  wireguard = {
    roles.controller.machines."vpn-server-1" = {
      settings.endpoint = "vpn1.example.com";
    };
    roles.controller.machines."vpn-server-2" = {
      settings.endpoint = "vpn2.example.com";
    };
    roles.peer.tags = [ "laptop" ];
  };

  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

Clan tries direct SSH first (priority 2000), then WireGuard (priority 1000), then Tor (priority 10).
