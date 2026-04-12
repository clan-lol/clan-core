# Internal SSL Services

Host clan-internal web services with HTTPS, accessible from any machine in your
clan via hostnames like `https://music.example.com`.

## Overview

Three services work together to make this possible:

- **[pki](/docs/services/official/pki)**: Generates TLS certificates for all
  internal endpoints using a static Root CA. No daemon required.
- **[dm-dns](/docs/services/official/dm-dns)**: Collects endpoint exports from
  all services and distributes DNS records via data-mesher, so every machine can
  resolve internal hostnames.
- **[data-mesher](/docs/services/official/data-mesher)**: The underlying
  transport that distributes DNS zone files (and other data) across your clan.

Machines must be able to reach each other via `<hostname>.<meta.domain>`. How
you achieve this is up to you - for example via
[yggdrasil](/docs/services/official/yggdrasil), a VPN, or any other networking
setup.

## How It Works

1. A service (e.g. navidrome) **exports an endpoint** like `music.example.com`
2. **dm-dns** collects all endpoint exports and generates DNS CNAME records,
   distributed via data-mesher
3. **pki** also collects all endpoint exports and generates TLS certificates
   signed by a clan-wide Root CA
4. All machines **trust the Root CA**, so HTTPS connections to internal services
   just work

The PKI architecture ensures that adding a new service or endpoint on one
machine does **not** require redeploying other machines:

- A **clan-wide Root CA** is created (shared generator, private key never leaves
  the operator machine)
- Each machine gets a **Host CA** signed by the Root CA
- Each endpoint gets a **certificate** signed by its Host CA
- All machines trust the Root CA, forming a complete chain of trust

If you use Caddy or nginx as a reverse proxy, pki automatically configures them
with the right certificates.

## Setup

### 1. Configure Data-Mesher

Data-mesher is required for distributing DNS records across your clan:

```nix
inventory.instances = {
  data-mesher = {
    roles.bootstrap.tags = [ "server" ];
    roles.default.tags = [ "all" ];
  };
};
```

### 2. Enable PKI and dm-dns

Add both services to your inventory, targeting all machines:

```nix
inventory.instances = {
  # Generates TLS certificates for all internal endpoints
  pki = {
    module.name = "pki";
    roles.default.tags = [ "all" ];
  };

  # Collects endpoint exports and distributes DNS records via data-mesher
  dm-dns = {
    module.name = "dm-dns";
    roles.push.machines.my-server = { };
    roles.default.tags = [ "all" ];
  };
};
```

### 3. Add a Service That Exports an Endpoint

Any service that exports an `endpoints.hosts` value will automatically get DNS
records and TLS certificates. For example, a navidrome music server:

```nix
inventory.instances = {
  navidrome = {
    module.name = "@pinpox/navidrome";
    roles.default.machines.my-server = {
      settings.host = "music.example.com";
    };
  };
};
```

After deploying, `https://music.example.com` will be reachable from any machine
in your clan with a valid, trusted TLS certificate.

## Writing a Service That Exports Endpoints

If you're authoring a service and want it to participate in this system, export
`endpoints` in your service manifest:

```nix
{ ... }:
{
  manifest.exports.out = [ "endpoints" ];

  roles.default = {
    perInstance =
      { mkExports, settings, ... }:
      {
        exports = mkExports {
          endpoints.hosts = [ settings.host ];
        };
        nixosModule =
          { ... }:
          {
            # Your service configuration here
          };
      };
  };
}
```

See the [exports guide](/docs/guides/services/exports) for details on the export
system.
