# clan-cli

The clan-cli contains the command line interface

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

## Run locally single-threaded for debugging

By default tests run in parallel using pytest-parallel.
pytest-parallel however breaks `breakpoint()`. To disable it, use this:

```console
pytest -n0 -s
```

You can also run a single test like this:

```console
pytest -n0 -s tests/test_secrets_cli.py::test_users
```

## Run tests in nix container

Run all impure checks

```console
nix run .#impure-checks
```

Run all checks

```console
nix flake check
```

## Debugging functions

Debugging functions can be found under `src/debug.py`
quite interesting is the function breakpoint_shell() which drops you into a shell
with the test environment loaded.
