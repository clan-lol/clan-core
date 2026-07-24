# P2P SSH via Iroh

:::admonition[Experimental]{type=danger}
This service is experimental and will change in the future.
:::

:::admonition[Security Notice]{type=warning}
Enabling this service exposes your machine's SSH service to anyone on the iroh network. The only protection against unauthorized access is SSH authentication itself. Before enabling this service, make sure SSH on all affected machines is configured securely: use private key authentication only and disable password login.
:::

The `p2p-ssh-iroh` service enables SSH access to machines behind NAT or firewalls without port forwarding, without a VPN, and without any public IP address. It uses [Iroh](https://github.com/n0-computer/dumbpipe)'s peer-to-peer QUIC transport to punch through NAT and establish an encrypted SSH tunnel from anywhere.

This service is not a VPN. It does not give machines private IP addresses or route general traffic between them. It is purely for SSH access: any machine with the `server` role can be reached via `clan ssh` or `clan machines update` from any machine that has an internet connection, regardless of NAT.

`p2p-ssh-iroh` has the highest priority of all Clan networking services (3000), meaning Clan tries it before anything else when connecting to a machine.

## When to Use

Use `p2p-ssh-iroh` when:

- You want SSH access to machines behind NAT from anywhere, with no infrastructure to set up
- You manage machines on networks where you have no control over firewall rules or port forwarding
- You want the simplest possible answer to "how do I reach this machine from the internet"

Do not use `p2p-ssh-iroh` as your only networking service if you also need machines to communicate with each other over a private network. For that, use ZeroTier, WireGuard, or Mycelium instead, and optionally add `p2p-ssh-iroh` on top for convenient SSH access.

## How It Works

When you assign the `server` role to a machine, Clan generates a stable Iroh secret key and a dumbpipe connection ticket for it. A systemd service runs continuously, forwarding incoming Iroh connections to the local SSH daemon. The ticket is stored as a var and distributed automatically so Clan knows how to reach the machine.

When you run `clan ssh my-machine` or `clan machines update my-machine`, Clan reads the ticket and establishes a P2P connection via Iroh's network. If a direct connection is possible, it connects directly. If both machines are behind NAT, Iroh falls back to relay servers to establish the connection.

## Roles

`p2p-ssh-iroh` has a single role: `server`. You can read more about [p2p-ssh-iroh's roles here](/docs/services/official/p2p-ssh-iroh#roles).

## Basic Example

```nix
# clan.nix
inventory.machines = {
  sally-laptop = { tags = [ "laptop" ]; };
  fred-laptop  = { tags = [ "laptop" ]; };
};

inventory.instances = {
  p2p-ssh-iroh = {
    roles.server.tags = [ "laptop" ];
  };
};
```

After running `clan vars generate` and deploying, both laptops are reachable via `clan ssh sally-laptop` from any internet-connected machine, even through NAT.

## Guide

To try out p2p-ssh-iroh, first follow one of the Getting Started Guides, up through and including installation.

Then, uncomment the part of `clan.nix` file that looks like this:

```nix
# p2p-ssh-iroh = {
#   roles.server.tags = [ "nixos" ];
# };
```

So it looks like this:

```nix
p2p-ssh-iroh = {
  roles.server.tags = [ "nixos" ];
};
```

(Use any tags that identify the machines you want to add this feature to.)

:::admonition[Experimental]{type=danger}
Because this feature is still in experimental stages, we do not recommend deleting the `sshd` entry unless you know exactly what you're doing. Doing so will remove your key from the `authorized_keys` file on the machine. If p2p-ssh-iroh fails, you will no longer be able to log in through `ssh` [without a password](../vars/intro-to-vars#your-first-var-the-root-password).
:::

Next, run the updater:

```bash
clan machines update test-machine
```

After updating, try logging into one of the machines that has the tag you added:

```bash
clan ssh test-machine
```

The `ssh` tool should first attempt to log in using a dumbpipe ticket specific to the machine:

```bash
$ clan ssh test-machine
using secret key <DUMBPIPE-KEY>
Machine test-machine reachable via p2p-ssh-iroh network
using secret key <DUMBPIPE-KEY>
using secret key <DUMBPIPE-KEY>
Last login: Sat Jun 27 19:59:16 2026 from 127.0.0.1

[root@test-machine:~]# 
```

If logging in through dumbpipe fails, you will see something similar to the following:

```text
using secret key 19488c82086866e9d95bf86140551844f4bcf3eb039ab48274551f753cdfa32b
Bad packet length 458961517.
ssh_dispatch_run_fatal: Connection to UNKNOWN port 65535: message authentication code incorrect
using secret key b0646b8071497a894eb06b7a72afbb57c42b33a177e3c2880fcee2cb19f22a9f
Bad packet length 458961517.
ssh_dispatch_run_fatal: Connection to UNKNOWN port 65535: message authentication code incorrect
```

followed by a successful attempt to log in through `sshd`.

## Combined with ZeroTier

Here is an example of where `p2p-ssh-iroh` provides SSH access to all machines, the `internet` service covers servers that have public addresses, and ZeroTier provides a private mesh network for inter-machine communication.

```nix
# clan.nix
inventory.machines = {
  web-server   = { tags = [ "server" ]; };
  db-server    = { tags = [ "server" ]; };
  sally-laptop = { tags = [ "laptop" ]; };
  fred-laptop  = { tags = [ "laptop" ]; };
};

inventory.instances = {
  # p2p-ssh-iroh on all machines for SSH access from anywhere
  p2p-ssh-iroh = {
    roles.server.tags = [ "all" ];
  };

  # Direct SSH for servers with public addresses (fast path)
  internet = {
    roles.default.machines."web-server".settings.host = "web.example.com";
    roles.default.machines."db-server".settings.host  = "db.example.com";
  };

  # ZeroTier for private inter-machine networking
  zerotier = {
    roles.controller.machines."web-server" = {};
    roles.peer.tags = [ "all" ];
  };
};
```

Clan tries `p2p-ssh-iroh` first (priority 3000) when connecting to any machine. For the servers, it will also try direct SSH (priority 2000) and ZeroTier (priority 900) as alternatives.
