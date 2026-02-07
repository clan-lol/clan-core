Lightweight PKI (Public Key Infrastructure) for clan networks using plain
OpenSSL. Unlike the `certificates` service which runs step-ca as a daemon, this
service is purely static - it only uses generators to create certificates with
no running services.

This allows you to host services inside your clan under the domain set via
[`meta.domain`](https://docs.clan.lol/reference/options/clan/#meta.domain) in
your inventory and access them over HTTPS. If you use Caddy or nginx as a
reverse proxy, pki automatically configures them with the right certificates -
your reverse proxy handles both internal clan domains and external domains
transparently, without any manual TLS setup.

## Usage

```nix
{
  inventory.instances = {
    pki = {
      module.name = "pki";
      roles.default.tags.all = { };
    };
  };
}
```

Services that export [`endpoints`](https://docs.clan.lol/reference/options/clan_service/#exports)
with hosts under your clan domain (e.g. `music.example.com`) will automatically
get TLS certificates generated and configured for Caddy or nginx.

## How it works

The service reads [`endpoints`](https://docs.clan.lol/reference/options/clan_service/#exports)
exports from other services on the same machine and generates a TLS certificate
for each internal host (i.e. hosts ending in `.${domain}`).

- A **clan-wide Root CA** is created as a shared generator (`deploy = false`,
  the private key never leaves the operator machine).
- Each machine with the `default` role gets **endpoint certificates** for every
  internal service it hosts, signed directly by the Root CA.
- All machines **trust the Root CA**, so any endpoint certificate is
  automatically verified through the chain of trust.
