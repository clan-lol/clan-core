This service is meant to be consumed by the UI / API, and exposes a JSON serializable interface to add packages to a machine over the inventory.

The example below demonstrates installing the "cbonsai" application to a machine named "server.

```
instances.packages = {
    roles.default.machines."server".settings = {
        packages = [ "cbonsai" ];
    };
};
```