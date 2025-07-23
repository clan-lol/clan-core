---
description = "DEPRECATED: Statically configure syncthing peers through clan"
---

# ⚠️ DEPRECATED

This module has been migrated to the new clanServices system.

Please use the new syncthing service instead:

```nix
{
  services.syncthing = {
    instances.default = {
      roles.peer.machines = {
        machine1 = { };
        machine2 = { };
        machine3 = {
          excludeMachines = [ "machine4" ];
        };
      };
    };
  };
}
```

The new service provides the same functionality with better integration into clan's inventory system.
