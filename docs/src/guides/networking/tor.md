# Tor Networking

The Tor service gives every machine a `.onion` address: a stable, cryptographically unique identifier that works anywhere Tor is running. Machines are reachable through the Tor network without public IP addresses, open firewall ports, or any DNS configuration.

Tor has the lowest priority (10) of all Clan networking services. Clan only uses it after every other configured networking service has failed. It is designed as a last-resort fallback: always available in theory, but the slowest option by a wide margin.

Use Tor when:

- You want a guaranteed fallback for machines that might be temporarily unreachable via direct SSH or VPN
- You have machines completely behind NAT with no public address and no VPN infrastructure
- You need to reach machines in environments with restrictive firewalls that block VPN protocols
- You want connections to remain possible even during major network disruptions

:::admonition[Experimental]{type=danger}
This service is experimental and will change in the future.
:::

## How It Works in Clan

When you assign a machine the `server` role, Clan generates a unique Ed25519 key pair for it and configures a Tor version 3 onion service. The `.onion` hostname is derived from the key pair and managed as a var. Clan distributes the hostname to any machine that needs to connect and uses it automatically when falling back to Tor.

By default, the hostname is stored as a secret var and does not appear in plaintext in your configuration. This is recommended: anyone who discovers the `.onion` address could attempt brute-force attacks against the SSH service.

## Roles

Tor provides two roles, client and server. You can read more about [Tor's roles here](/docs/services/official/tor#roles).

## Basic Example

```nix
# clan.nix
inventory.instances = {
  tor = {
    roles.server.tags = [ "all" ];
  };
};
```

This is all you need. After running `clan vars generate` and deploying, every machine has a Tor onion address and Clan can use it as a fallback automatically.

## Another Example

This setup uses the `internet` service for primary connectivity and Tor as a fallback for all machines. The admin laptop gets the `client` role because it frequently connects to other machines and benefits from a persistent Tor proxy.

```nix
# clan.nix
inventory.machines = {
  web-server    = { tags = [ "server" ]; };
  db-server     = { tags = [ "server" ]; };
  backup-server = { tags = [ "server" ]; };
  admin-laptop  = { tags = [ "laptop" ]; };
};

inventory.instances = {
  # Primary: direct SSH for servers with public addresses
  internet = {
    roles.default.machines."web-server".settings.host    = "web.example.com";
    roles.default.machines."db-server".settings.host     = "db.example.com";
    roles.default.machines."backup-server".settings.host = "backup.example.com";
  };

  # Fallback: Tor for all machines
  tor = {
    roles.server.tags = [ "all" ];

    # Keep a persistent Tor proxy on the admin laptop
    roles.client.machines."admin-laptop" = {};
  };
};
```

In this case, we have two services, Internet and Tor. By default, Internet has a higher priority, meaning when connecting, Clan will first try direct SSH through the Internet service. If a server is unreachable at its public address, Clan falls back to Tor.

## Guide

To try out the Tor feature, create two cloud servers using the initial part of the Getting Started guide for a cloud ([such as AWS](../../getting-started/getting-started-aws) or [or Heztner](../../getting-started/getting-started-hetzner)), including adding your id_ed25519 key pair.

Create the clan, calling it CLAN-TOR:

```bash
nix run https://clan.lol/install/{{ version }} --refresh -- init
cd CLAN-TOR
direnv allow
```

and then create the two machines:

```bash
clan machines create web-server
clan machines create db-server
```

Update clan.nix to look like the following:

```nix
{
  # Ensure this is unique among all clans you want to use.
  meta.name = "CLAN-TOR";
  meta.domain = "clantor.lol";

  inventory.machines = {
    web-server = {
      tags = [ "test" ];
    };
    db-server = {
      tags = [ "test" ];
    };
  };

  inventory.instances = {

    internet = {
      roles.default.machines."web-server" = {
        settings.host = "44.243.115.151"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS
        settings.user = "root";
      };
      roles.default.machines."db-server" = {
        settings.host = "35.95.10.21"; # REPLACE WITH YOUR MACHINE'S IP ADDRESS
        settings.user = "root";
      };
    };

    tor = {
      roles.server.tags = [ "all" ];

      # Keep a persistent Tor proxy on the admin laptop
      roles.client.machines."web-server" = { };
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
        "admin-machine-1" =
          "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAZGMNlooljzJfmzQKaVcmj4tRYW+gqBIfdWbG0NU3XL freckleface@freckleface--Laptop";
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

  # Additional NixOS configuration can be added here.
  # machines/server/configuration.nix will be automatically imported.
  # See: https://clan.lol/docs/unstable/guides/inventory/autoincludes
  machines = {
    # test-machine = { config, ... }: {
    #   environment.systemPackages = [ pkgs.asciinema ];
    # };
  };
}
```

Gather the hardware configuration:

```bash
clan machines init-hardware-config web-server
clan machines init-hardware-config db-server
```

(For AWS, you'll add on `--target-host ubuntu@<IP-ADDRESS>` to each line.)

Add a disk configuration using the usual approach of re-running each command with the generated output added inside double-quotes:

```bash
clan templates apply disk ext4-single-disk web-server --set mainDisk ""
clan templates apply disk ext4-single-disk db-server --set mainDisk ""
```

And finally, install:

```bash
clan machines install web-server
clan machines install db-server
```

Or, if you already installed, update:

```bash
clan machines update
```

If you get an error about sandboxing:

```bash
clan vars generate web-server --no-sandbox
clan vars generate db-server --no-sandbox
```

Now you can obtain the .onion addresses for the two servers:

```bash
clan vars get web-server tor_tor/hostname
clan vars get db-server tor_tor/hostname
```

You will see two ".onion" lines similar to the following:

```text
kfobkkl3qexgyvzkwvj47f2gwo4vzgnmgk2xrkasmpgext2rblo6pgid.onion
tttwjmew6syhhqixakmv55jmbcsogeyar3anryfw4jaenmyzu7xemlqd.onion
```

Next, to see if the onion service is running, ssh into one of the two servers and type:

```bash
systemctl status tor
```

Your should see output that includes the first few lines looking similar to this, including the words "Active: active (running)".

```text
tor.service - Tor Daemon
     Loaded: loaded (/etc/systemd/system/tor.service; enabled; preset: ignored)
     Active: active (running) since Thu 2026-07-02 18:43:39 UTC; 10min ago
```

Exit back to your own computer. Now you can see if Tor was installed successfully by using `torsocks` to SSH into one of the two servers using its .onion address:

```bash
torsocks ssh root@kfobkkl3qexgyvzkwvj47f2gwo4vzgnmgk2xrkasmpgext2rblo6pgid.onion
```

You will then see a normal SSH shell, from which you can exit:

```text
[root@web-server:~]# exit
```

Tip: If you need to install torsocks, you can do so with:

```bash
sudo apt update
sudo apt install torsocks tor -y
```

## Port Mapping

By default, the onion service maps port 22 to port 22. If your SSH daemon listens on a different port, adjust the mapping:

```nix
# clan.nix
inventory.instances = {
  tor = {
    roles.server.machines."my-server" = {
      settings.portMapping = [
        { port = 22; target.port = 2222; }
      ];
    };
  };
};
```

This exposes port 22 on the onion address and forwards it to port 2222 on the machine.

## Secret Hostnames

The `secretHostname` setting defaults to `true`, keeping the `.onion` address out of plaintext configuration. This is strongly recommended for any machine exposed to the internet.

In a controlled internal environment where you are certain exposure of the address isn't a concern, you can disable it:

```nix
# clan.nix
inventory.instances = {
  tor = {
    roles.server.machines."internal-machine" = {
      settings.secretHostname = false;
    };
  };
};
```

Clan handles distributing onion addresses to machines that need them. You don't manage or share the hostname yourself.
