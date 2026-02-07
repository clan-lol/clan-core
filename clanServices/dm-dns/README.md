!!! Danger "Experimental"
    This service is experimental and will change in the future.

---

This service provides distributed DNS zone propagation for clan networks. It
collects `endpoints` exports from all services, generates CNAME zone entries,
and distributes them via data-mesher. Each machine runs unbound to resolve
clan-internal hostnames.

In practice, this means a service which provides some endpoint (e.g. a web UI)
at `https://myservice.<clan domain>` is reachable from any machine in your clan
with this service enabled. This allows easely hosting clan-internal services.

It is recommended to combine this service with the [pki service](../pki/README.md), to
have your internal services be secured with SSL.

This service requires the following dependencies to work:
- [**data-mesher**](../data-mesher/README.md): Must be configured and running on all machines
- **endpoints exports**: Other services must export [`endpoints.hosts`](https://docs.clan.lol/reference/options/clan_service/#exports) for DNS
  entries to be generated

## Usage

```nix
inventory.instances = {
  dm-dns = {
    module.name = "dm-dns";
    roles.default.tags = [ "all" ];
  };
};
```

## Architecture

- Collects all `endpoints` exports across the clan
- Generates unbound zone entries (CNAME records) mapping endpoint hostnames to
  machine hostnames
- Distributes zone files via data-mesher's signed file mechanism
- Each node runs unbound on port 5353, with systemd-resolved routing the clan
  domain to it
- A systemd path unit watches for zone file changes and reloads unbound
  automatically


## Signing and Pushing Zone Files

The service generates a signing key pair (`dm-dns-signing-key`) and a zone file
(`dm-dns`) via clan vars generators. To distribute the zone file via
data-mesher, you need a script that signs and pushes the zone file using the
private signing key.

Since the method for accessing the private signing key depends on your secrets
backend (e.g. `passage`, `sops`, `agenix`), the push script is **not** included
in this service. Instead, add your own script via `extraModules` in the
inventory:

```nix
inventory.instances.dm-dns = {
  module.name = "dm-dns";
  roles.default.tags = [ "all" ];
  roles.default.extraModules = [
    ({ config, pkgs, ... }: {
      environment.systemPackages = [
        (pkgs.writeShellApplication {
          name = "dm-send-dns";
          runtimeInputs = [ config.services.data-mesher.package ];
          text = ''
            data-mesher file update \
              "${config.clan.core.vars.generators.dm-dns.files."zone.conf".path}" \
              --url http://localhost:7331 \
              --key "$(passage show clan-vars/shared/dm-dns-signing-key/signing.key)" \
              --name "dns/cnames"
          '';
        })
      ];
    })
  ];
};
```

The example above uses `passage` as the secrets backend. Replace the `passage
show ...` call with the appropriate command for your secrets backend.
