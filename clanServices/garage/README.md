[Garage](https://garagehq.deuxfleurs.fr/) is an open-source, S3-compatible distributed object storage service for self-hosting.

This module provisions a single-instance S3 bucket. To customize its behavior, set `services.garage.settings` in your Nix configuration.

Example configuration:
```
instances = {
    garage = {
        roles.default.machines."server" = {};
    };
};
```
