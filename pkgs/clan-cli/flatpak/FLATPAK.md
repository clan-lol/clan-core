# Flatpak Documentation


## Installing locally

You can install the package locally through `flatpak-builder`:
```sh
flatpak-builder --user --install --force-clean build-dir org.clan.cli.yml
```

## Debugging

```sh
flatpak run --devel --command=sh org.clan.cli
```

Replace `org.clan.cli` with the desired identifier.
Now you can run commands inside the sandbox, for example:
```sh
[📦 org.clan.cli clan-cli-flatpak]$ strace -f -o strace.log clan vms run syncthing-peer1
```
