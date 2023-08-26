# clan-cli

The clan-cli contains the command line interface as well as the graphical webui through the `clan webui` command.

## Hacking on the cli

We recommend setting up [direnv](https://direnv.net/) to load the developement with nix.
If you do not have it set up you can also use `nix develop` directly like this:

```
use flake .#clan-cli --builders ''
```

After you can use the local bin wrapper to test things in the cli:

```
./bin/clan
```

## Hacking on the webui

By default the webui is build from a tarball available https://git.clan.lol/clan/-/packages/generic/ui/.
To start a local developement environment instead, use the `--dev` flag:

```
./bin/clan webui --dev
```

This will spawn two webserver, a python one to for the api and a nodejs one that rebuilds the ui on the fly.
