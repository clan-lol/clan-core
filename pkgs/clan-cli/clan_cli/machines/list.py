import argparse
import json
import logging
from pathlib import Path

from clan_cli.api import API

from ..cmd import run_no_stdout
from ..nix import nix_config, nix_eval

log = logging.getLogger(__name__)


@API.register
def list_machines(flake_url: str | Path, debug: bool) -> list[str]:
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

    proc = run_no_stdout(cmd)

    res = proc.stdout.strip()
    return json.loads(res)


def list_command(args: argparse.Namespace) -> None:
    flake_path = Path(args.flake).resolve()
    for name in list_machines(flake_path, args.debug):
        print(name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
