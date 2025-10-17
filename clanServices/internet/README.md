🚧🚧🚧 Experimental 🚧🚧🚧

Use at your own risk.

We are still refining its interfaces, instability and breakages are expected.

---

This module is part of Clan's [networking interface](https://docs.clan.lol/guides/networking/networking/).

Clan's networking module automatically manages connections across available network transports and falls back intelligently. When you run `clan ssh` or `clan machines update`, Clan attempts each configured network in priority order until a connection succeeds.

The example below shows how to configure a domain so server1 is reachable over the clearnet. By default, the `internet` module has the highest priority among networks.

```nix
  inventory.instances = {
        # Direct SSH with fallback support
        internet = {
            roles.default.machines.server1 = {
                settings.host = "server1.example.com";
            };
            roles.default.machines.server2 = {
                settings.host = "192.168.1.100";
            };
        };
};
```
