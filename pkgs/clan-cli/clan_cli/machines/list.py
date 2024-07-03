import argparse
import json
import logging
from pathlib import Path

from clan_cli.api import API
from clan_cli.inventory import Machine

from ..cmd import run_no_stdout
from ..nix import nix_eval

log = logging.getLogger(__name__)


@API.register
def list_machines(flake_url: str | Path, debug: bool = False) -> dict[str, Machine]:
    cmd = nix_eval(
        [
            f"{flake_url}#clanInternals.inventory.machines",
            "--json",
        ]
    )

    proc = run_no_stdout(cmd)

    res = proc.stdout.strip()
    data = {name: Machine.from_dict(v) for name, v in json.loads(res).items()}
    return data


def list_command(args: argparse.Namespace) -> None:
    flake_path = args.flake.path
    for name in list_machines(flake_path, args.debug).keys():
        print(name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
