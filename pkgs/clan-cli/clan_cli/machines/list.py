import argparse
import json
import logging
from pathlib import Path

from clan_cli.api import API

from ..cmd import Log, run
from ..nix import nix_config, nix_eval

log = logging.getLogger(__name__)


@API.register
def list_machines(
    debug: bool,
    flake_url: Path | str,
) -> list[str]:
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{flake_url}#clanInternals.machines.{system}",
            "--apply",
            "builtins.attrNames",
            "--json",
        ]
    )

    if not debug:
        proc = run(cmd, log=Log.NONE)
    else:
        proc = run(cmd)

    res = proc.stdout.strip()
    return json.loads(res)


def list_command(args: argparse.Namespace) -> None:
    for machine in list_machines(args.debug, Path(args.flake)):
        print(machine)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
