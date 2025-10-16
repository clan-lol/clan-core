This module is part of Clan's [networking interface](https://docs.clan.lol/guides/networking/networking/).

Clan's networking module automatically manages connections across available network transports and falls back intelligently. When you run `clan ssh` or `clan machines update`, Clan attempts each configured network in priority order until a connection succeeds.

The example below configures all your nixos machines to be reachable over the Tor network. By default, the `tor` module has the lowest priority among networks, as it's the slowest.

```nix
  inventory.instances = {
        # Fallback: Secure connections via Tor
        tor = {
            roles.server.tags.nixos = { };
        };
};
```