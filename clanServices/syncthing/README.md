This service configures Syncthing to continuously synchronize a folder peer-to-peer across your machines.

Example configuration:

```nix
{
  instances.syncthing = {
    roles.peer.tags.all = { };
    roles.peer.settings.folders = {
      documents = {
        path = "/home/youruser/syncthing/documents";
      };
    };
  };
}
```

Notes:
- Each key under `folders` is a folder ID (an arbitrary identifier for Syncthing).
- Prefer absolute paths (example shown). `~` may work in some environments but can be ambiguous in service contexts.


## Documentation
See the official Syncthing docs: https://docs.syncthing.net/
