## Usage

```nix
{
      instances.syncthing = {
        roles.peer.tags.all = { };
        roles.peer.settings.folders = {
          documents = {
            path = "~/syncthing/documents";
          };
        };
      };
}
```

Now the folder `~/syncthing/documents` will be shared with all your machines.


## Documentation 
Extensive documentation is available on the [Syncthing](https://docs.syncthing.net/) website.
