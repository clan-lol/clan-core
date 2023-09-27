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

## Run webui directly

Useful for vscode run and debug option

```bash
python -m clan_cli.webui --reload --no-open
```

Add this `launch.json` to your .vscode directory to have working breakpoints in your vscode editor.

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Clan Webui",
      "type": "python",
      "request": "launch",
      "module": "clan_cli.webui",
      "justMyCode": true,
      "args": ["--reload", "--no-open", "--log-level", "debug"]
    }
  ]
}
```

## Run locally single-threaded for debugging

By default tests run in parallel using pytest-parallel.
pytest-parallel however breaks `breakpoint()`. To disable it, use this:

```console
pytest --workers "" -s
```

You can also run a single test like this:

```console
pytest --workers "" -s tests/test_secrets_cli.py::test_users
```
