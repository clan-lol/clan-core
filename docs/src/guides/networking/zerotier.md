# ZeroTier Networking

ZeroTier creates a private, encrypted mesh network between your machines. Once configured, every machine gets an automatically assigned IP address and can reach every other machine on the network, regardless of NAT, firewalls, or physical location. You don't need public IP addresses, open firewall ports, or an account on zerotier.com. Clan runs its own controller.

Use ZeroTier when your machines are behind NAT, when laptops travel between networks, or when you want an always-on private network that handles connectivity for you without exposing anything to the public internet.

## How It Works in Clan

Clan manages the entire ZeroTier setup through the vars system. When you run `clan vars generate`, Clan generates a unique ZeroTier identity for each machine and derives a stable IP address from it. No manual IP assignment is needed.

The ZeroTier service has a priority of 900. If you also configure the `internet` service (priority 2000), Clan tries direct SSH first and falls back to ZeroTier if that fails.

## Roles

The ZeroTier service has three roles: `controller`, `peer`, and `moon`. You can read more about [ZeroTier's roles here](/docs/services/official/zerotier#roles).

## Basic Example

```nix
# clan.nix
inventory.machines = {
  my-server     = { tags = [ "server" ]; };
  sally-laptop  = { tags = [ "laptop" ]; };
  fred-laptop   = { tags = [ "laptop" ]; };
};

inventory.instances = {
  zerotier = {
    roles.controller.machines."my-server" = {};
    roles.peer.tags = [ "all" ];
  };
};
```

`my-server` is the controller. All machines, including `my-server` itself via the `all` tag, join as peers. Clan generates ZeroTier identities and IPs for every machine automatically.

## Guide

To try out the ZeroTier feature, create three cloud servers using the initial part of the Getting Started guide for a cloud ([such as AWS](../../getting-started/getting-started-aws) or [or Heztner](../../getting-started/getting-started-hetzner)), including adding your id_ed25519 key pair.

Create the clan, calling it CLAN-ZT:

```bash
nix run https://clan.lol/install/{{ version }} --refresh -- init
cd CLAN-ZT
direnv allow
```

and then create the three machines:

```bash
clan machines create my-controller
clan machines create peer1
clan machines create peer2
```

Update `clan.nix` to look like the following:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "CLAN-ZT";
  meta.domain = "clanzt.lol";

  inventory.machines = {
    my-controller = {
      tags = [ "controller" ];
    };
    peer1 = {
      tags = [ "peer" ];
    };
    peer2 = {
      tags = [ "peer" ];
    };
  };

  inventory.instances = {

    internet = {
      roles.default.machines."my-controller" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR CONTROLLER MACHINE'S IP ADDRESS
        settings.user = "root";
      };
      roles.default.machines."peer1" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR FIRST PEER MACHINE'S IP ADDRESS
        settings.user = "root";
      };
      roles.default.machines."peer2" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR SECOND PEER MACHINE'S IP ADDRESS
        settings.user = "root";
      };
    };

    zerotier = {
      # Specify the controller here
      roles.controller.machines."my-controller" = { };

      # Specify which machines become part of ZeroTier
      roles.peer.tags = [ "all" ];
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

    # Docs: https://clan.lol/docs/unstable/services/official/p2p-ssh-iroh
    # Status experimental
    # Firewall-traversing SSH access via encrypted QUIC streams
    # p2p-ssh-iroh = {
    #   roles.server.tags = [ "nixos" ];
    # };
  };
}
```

Update the IP addresses in the `clan.nix` file where noted, and add in your authorized key.

Gather the hardware configurations:

```bash
clan machines init-hardware-config my-controller
clan machines init-hardware-config peer1
clan machines init-hardware-config peer2
```

(For AWS, you'll add on `--target-host ubuntu@<IP-ADDRESS>` to each line.)

Add a disk configuration using the usual approach of re-running each command with the generated output added inside double-quotes:

```bash
clan templates apply disk ext4-single-disk my-controller --set mainDisk ""
clan templates apply disk ext4-single-disk peer1 --set mainDisk ""
clan templates apply disk ext4-single-disk peer2 --set mainDisk ""
```

Now generate vars. This generates the necessary setup for ZeroTier. Start with controller:

```bash
clan vars generate my-controller
```

Then do the peers:

```bash
clan vars generate peer1
clan vars generate peer2
```

(Note that if you get messages that an identity doesn't exist, go ahead and run the vars generate command for the machine specified in the error message. Then loop back and start with the controller again, and then with peer1 again.)

Next install the controller first:

```text
clan machines install my-controller
```

Then install the peers:

```text
clan machines install peer1
```

```text
clan machines install peer2
```

Here's how you discover the IPv6 addresses for each of the three machines, used by ZeroTier:

```text
clan vars get my-controller zerotier-ip-my-controller-zerotier/ip
clan vars get peer1 zerotier-ip-my-controller-zerotier/ip
clan vars get peer2 zerotier-ip-my-controller-zerotier/ip
```

Now you can try pinging using these IPv6 addresses. `SSH` into `peer1` and then, from peer1, ping peer2:

```text
ping <PEER2-IPv6-ADDRESS>
```

Then to be sure, ping the above from a computer not on the ZeroTier network. You'll get a message that the network is unreachable.

## Adding External Machines

If you have devices outside your Clan inventory that you want to admit to the ZeroTier network (a phone, a colleague's laptop, a cloud VM), you can allow them on the controller by node ID. The node ID of any ZeroTier device is shown by running `zerotier-cli info` on that device.

On Linux, first install ZeroTier:

```bash
curl -s 'https://raw.githubusercontent.com/zerotier/ZeroTierOne/main/doc/contact%40zerotier.com.gpg' | gpg --import && \
if z=$(curl -s 'https://install.zerotier.com/' | gpg); then echo "$z" | sudo bash; fi
```

Note the ID at the end of the "Success!" message, e.g.:

```text
*** Success! You are ZeroTier address [ 0c27a66feb ].
```

Now obtain the network ID:

```bash
clan vars get my-controller zerotier-network-zerotier/network-id
```

For example:

```text
0d00bbf7d9b17658
```

Add this to inside the zerotier attribute set:

```nix
    zerotier = {
      # Specify the controller here
      roles.controller.machines."my-controller" = {
        settings.allowedIds = [ "aaabbbccc00s" "abc1234567" ]; # node IDs from `zerotier-cli info` on the outside machines
      };

      # Specify which machines become part of ZeroTier
      roles.peer.tags = [ "all" ];
    };
```

Then update controller:

```bash
clan machines update my-controller
```

Then try pinging one of the other computers from the computer that joined:

```text
ping6 fd0d:bb:f7d9:b176:5899:93bf:df38:8f4d
```

You can also allow external machines by their ZeroTier IP address if you already know it:

```nix
roles.controller.machines."my-controller" = {
  settings.allowedIps = [ "fd5d:bbe3:cbc5:fe6b:f699:935d:bbe3:cbc5" ];
};
```

## Guide: Moon Relay Demo

If you have computers managed by a Clan that are on different networks or behind NATs, a Relay (also called Moon) is helpful. Instead of opening the controller up to the world, you allow the machines to connect to a computer whose job is to relay information into the network.

For this guide we'll start with a new Clan and set of machines. Follow one of the Cloud getting started guides ([AWS](../../getting-started/getting-started-aws), [Hetzner](../../getting-started/getting-started-hetzner), or [Google Cloud](../../getting-started/getting-started-google)) and create two servers:

1. One for the controller
2. One for the relay through which servers out-of-network (for example, laptops behind a NAT) can connect

Follow the guides up to and including where you copy the id_ed25519 key pair over.

:::admonition[Important]{type=important}
In addition to opening port 22 (SSH) for incoming traffic, you'll also need to open UDP port 9993:

* The relay needs to accept incoming UDP 9993 traffic from *anywhere*
* The controller needs to accept incoming UDP 9993 traffic, but only from *the relay*
:::

Depending on your cloud platform, to accomplish the above, you'll need two different security groups or firewall rules.

:::admonition[Important]{type=important}
The relay needs a permanent IP address. (Or, if you're just trying this out, the IP address needs to remain the same throughout the exercise.)
:::

Then, with a laptop, follow the [VirtualBox Getting Started Guide](../../getting-started/getting-started-virtualbox) to create a virtual machine that, for this demonstration, will represent a laptop.

Next, create the Clan:

```bash
nix run https://clan.lol/install/{{ version }} --refresh -- init
```

and call it `CLAN-MOON`. Then `cd` into the directory and allow direnv; then create three machines:

```bash
cd CLAN-MOON
direnv allow
clan machines create my-controller
clan machines create my-relay
clan machines create my-laptop
```

Then update your `clan.nix` file to look like the following, filling in the IP addresses and key:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "CLAN-MOON";
  meta.domain = "clanmoon.lol";

  inventory.machines = {
    my-controller = {
      tags = [ "controller" ];
    };
    my-relay = {
      tags = [ "peer" ];
    };
    my-laptop = {
      tags = [ "peer" ];
    };

  };

  inventory.instances = {

    internet = {
      roles.default.machines."my-controller" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS
        settings.user = "root";
      };
      roles.default.machines."my-relay" = {
        settings.host = "<IP-ADDRESS>"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS
        settings.user = "root";
      };
      roles.default.machines."my-laptop" = {
        settings.host = "127.0.0.1"; # Use NAT with port forwarding
        settings.user = "root";
        settings.port = 2222;
      };
    };

    zerotier = {
      roles.controller.machines."my-controller" = { };
      roles.moon.machines."my-relay" = {
        settings.stableEndpoints = [ "<IP-ADDRESS>" ]; # Fill in with the Relay's public IP address
      };
      roles.peer.tags = [ "all" ];
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

Then do the hardware config:

```bash
clan machines init-hardware-config my-controller
clan machines init-hardware-config my-relay
clan machines init-hardware-config my-laptop
```

(If you're using AWS for the controller and relay, you'll add on `--target-host ubuntu@<IP-ADDRESS>` to those two lines.)

Then add a disk for each machine, filling in the final quotes:

```bash
clan templates apply disk ext4-single-disk my-controller --set mainDisk ""
clan templates apply disk ext4-single-disk my-relay --set mainDisk ""
clan templates apply disk ext4-single-disk my-laptop --set mainDisk ""
```

Next, do a vars generate on each, starting with my-controller; you might need to repeat my-controller after finishing the other three:

```bash
clan vars generate my-controller
clan vars generate my-relay
clan vars generate my-laptop
```

Or, with --no-sandbox:

```bash
clan vars generate my-controller --no-sandbox
clan vars generate my-relay --no-sandbox
clan vars generate my-laptop --no-sandbox
```

At this point, Clan and ZeroTier have already created IPv6 addresses for each machine, even though you haven't installed Clan yet on any of them. You can obtain them as follows:

```bash
clan vars get my-controller zerotier-ip-my-controller-zerotier/ip
clan vars get my-relay zerotier-ip-my-relay-zerotier/ip
clan vars get my-laptop zerotier-ip-my-laptop-zerotier/ip
```

Now you're ready to install. Install in this order:

```bash
clan machines install my-controller
clan machines install my-relay
clan machines install my-laptop
```

Now try `SSH`ing into each; as before, you'll probably get a message that you have to run ssh-keygen for each before you can SSH in.

Inside each, try pinging each other IPv6 address.

Then, inside the `my-laptop` machine, look at the output from this:

```bash
zerotier-cli peers
```

You should see one MOON with link type DIRECT, and at least one LEAF with link type RELAY:

```text
<ztaddr>   <ver>  <role> <lat> <link>   <lastTX> <lastRX> <path>
0575c8a9f4 1.16.0 MOON      56 DIRECT   3840     3784     35.88.39.174/48295
2cfda73752 -      LEAF      -1 RELAY
62f865ae71 -      LEAF      -1 RELAY
778cde7190 -      PLANET    72 DIRECT   3975     14316    103.195.103.66/9993
cafe04eba9 -      PLANET   214 DIRECT   3975     19175    84.17.53.155/9993
cafe80ed74 -      PLANET    41 DIRECT   3975     3897     185.152.67.145/9993
cafe9efeb9 -      LEAF      -1 RELAY
cafefd6717 -      PLANET   155 DIRECT   3975     14233    79.127.159.187/9993
```

ZeroTier handles outbound NAT traversal automatically. In a real-world production deployment, users won't need to change anything on their local router or firewall outbound settings; they only need to ensure their corporate firewalls don't aggressively block outgoing UDP traffic entirely.

## Pairing ZeroTier with Other Networking Services

ZeroTier works well alongside the `internet` service for direct access and Tor as a final fallback:

```nix
# clan.nix
inventory.instances = {
  internet = {
    roles.default.machines."controller-server".settings.host = "controller.example.com";
  };

  zerotier = {
    roles.controller.machines."controller-server" = {};
    roles.peer.tags = [ "all" ];
  };

  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

In this example, because by default the Internet service has a higher priority than ZeroTier or tor, Clan tries direct SSH first as part of the Internet service; if that fails, it then tries ZeroTier; then, finally, Tor. The controller is always reachable via the `internet` service even before ZeroTier is established on a new machine.
