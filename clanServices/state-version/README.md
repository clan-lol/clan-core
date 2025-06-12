This service generates the `system.stateVersion` of the nixos installation
automatically.

Possible values:
[system.stateVersion](https://search.nixos.org/options?channel=unstable&show=system.stateVersion&from=0&size=50&sort=relevance&type=packages&query=stateVersion)

## Usage

The following configuration will set `stateVersion` for all machines:

```
inventory.instances = {
  state-version = {
    module = {
      name = "state-version";
      input = "clan";
    };
    roles.default.tags.all = { };
  };
```

## Migration

If you are already setting `system.stateVersion`, either let the automatic
generation happen, or trigger the generation manually for the machine. The
service will take the specified version, if one is already supplied through the
config.

To manually generate the version for a specified machine run:

```
clan vars generate [MACHINE]
```

If the setting was already set, you can then remove `system.stateVersion` from
your machine configuration. For new machines, just import the service as shown
above.
