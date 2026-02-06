A common use case you might have is to host services and applications which are
only reachable within your clan.

This guide explains how to set up such secure, clan-internal web services using
a custom top-level domain (TLD) with SSL certificates.

Your services will be accessible only within your Clan network and secured with
proper SSL certificates that all Clan machines trust.

## Overview

By combining the `coredns` and `certificates` Clan services, you can:

- Create a custom TLD for your Clan (e.g. `.c`)
- Host internal web services accessible via HTTPS (e.g. `https://api.c`, `https://dashboard.c`)
- Automatically provision and trust SSL certificates across all Clan machines
- Keep internal services secure and isolated from the public internet

The setup uses two Clan services working together:

- **coredns service**: Provides DNS resolution for your custom TLD within the Clan
- **certificates service**: Creates a certificate authority (CA) and issues SSL certificates for your TLD

### DNS Resolution Flow

1. A Clan machine tries to access `https://service.c`
2. The machine queries its local DNS resolver (unbound)
3. For `.c` domains, the query is forwarded to your Clan's CoreDNS server. All
   other domains will be resolved as usual.
4. CoreDNS returns the IP address of the machine hosting the service
5. The machine connects directly to the service over HTTPS
6. The SSL certificate is trusted because all machines trust your Clan's CA

## Step-by-Step Setup

The following setup assumes you have a VPN (e.g. ZeroTier) already running. The
IPs configured in the options below will probably the ZeroTier IPs of the
respective machines.

### Configure the CoreDNS Service

The CoreDNS service has two roles:
- `server`: Runs the DNS server for your custom TLD
- `default`: Makes machines use the DNS server for TLD resolution and allows exposing services

Add this to your inventory:

```nix
inventory = {
  machines = {
    dns-server = { }; # Machine that will run the DNS server
    web-server = { }; # Machine that will host web services
    client = { };     # Any other machines in your clan
  };

  instances = {
    coredns = {

      # Add the default role to all machines
      roles.default.tags = [ "all" ];

      # DNS server for the .c TLD
      roles.server.machines.dns-server.settings = {
        ip = "192.168.XXX.XXX";
        tld = "c";
      };

      # Machine hosting services (e.g. ca.c and admin.c)
      roles.default.machines.web-server.settings = {
        ip = "192.168.XXX.XXX";
        services = [ "ca" "admin" ];
      };
    };
  };
};
```

### Configure the Certificates Service

The certificates service also has two roles:
- `ca`: Sets up the certificate authority on a server
- `default`: Makes machines trust the CA and allows them to request certificates

Add this to your inventory:

```nix
inventory = {
  instances = {
    # coredns configuration from above

    certificates = {

      # Set up CA for .c domain
      roles.ca.machines.dns-server.settings = {
        tlds = [ "c" ];
        acmeEmail = "admin@example.com";
      };

      # Add default role to all machines to trust the CA
      roles.default.tags = [ "all" ];
    };
  };
};
```

### Complete Example Configuration

Here's a complete working example:

```nix
nventory = {
  machines = {
    caserver = { };  # DNS server + CA + web services
    webserver = { }; # Additional web services
    client = { };    # Client machine
  };

  instances = {
    coredns = {

      # Add the default role to all machines
      roles.default.tags = [ "all" ];

      # DNS server for the .c TLD
      roles.server.machines.caserver.settings = {
        ip = "192.168.XXX.XXX";
        tld = "c";
      };

      # Machine hosting https://ca.c (CA for SSL)
      roles.default.machines.caserver.settings = {
        ip = "192.168.XXX.XXX";
        services = [ "ca" ];
      };

      # Machine hosting https://blub.c (internal web service)
      roles.default.machines.webserver.settings = {
        ip = "192.168.XXX.XXX";
        services = [ "blub" ];
      };
    };

    # Provide https for the .c top-level domain
    certificates = {

      roles.ca.machines.caserver.settings = {
        tlds = [ "c" ];
        acmeEmail = "admin@example.com";
      };

      roles.default.tags = [ "all" ];
    };
  };
};
```

## Testing Your Configuration

DNS resolution can be tested with:

```bash
# On any clan machine, test DNS resolution
nslookup ca.c
nslookup blub.c
```

You should also now be able to visit `https://ca.c` to access the certificate authority or visit `https://blub.c` to access your web service.

## Troubleshooting

### DNS Resolution Issues

1. **Check if DNS server is running**:
```bash
# On the DNS server machine
systemctl status coredns
```

2. **Verify DNS configuration**:
```bash
# Check if the right nameservers are configured
cat /etc/resolv.conf
systemctl status systemd-resolved
```

3. **Test DNS directly**:
```bash
# Query the DNS server directly
dig @192.168.XXX.XXX ca.c
```

### Certificate Issues

1. **Check CA status**:
```bash
# On the CA machine
systemctl status step-ca
systemctl status nginx
```

2. **Verify certificate trust**:
```bash
# Test certificate trust
curl -v https://ca.c
openssl s_client -connect ca.c:443 -verify_return_error
```

3. **Check ACME configuration**:
```bash
# View ACME certificates
ls /var/lib/acme/
journalctl -u acme-ca.c.service
```
