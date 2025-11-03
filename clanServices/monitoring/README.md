!!! Danger "Experimental"
    This service is experimental and will change in the future.

## Usage

```
inventory.instances = {
    monitoring = {
      module.name = "monitoring";
      roles.telegraf.tags.all = {
        settings.interfaces = [ "wg-clan" ];
      };
    };
  };
```

This service will eventually set up a monitoring stack for your clan. For now,
only a telegraf role is implemented, which exposes the currently deployed
version of your configuration, so it can be used to check for required updates.

