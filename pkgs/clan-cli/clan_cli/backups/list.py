import argparse
import pprint
from pathlib import Path
from typing import Optional

from ..errors import ClanError


def list_backups(flake_dir: Path, machine: Optional[str] = None, provider: Optional[str] = None) -> dict[str, dict[str, list[str]]]:
    dummy_data = {
        "testhostname": {
            "borgbackup": [
                "2021-01-01T00:00:00Z",
                "2022-01-01T00:00:00Z",
                "2023-01-01T00:00:00Z",
            ],
            "restic" : [
                "2021-01-01T00:00:00Z",
                "2022-01-01T00:00:00Z",
                "2023-01-01T00:00:00Z",
            ],
        },
        "another host": {
            "borgbackup": [
                "2021-01-01T00:00:00Z",
                "2022-01-01T00:00:00Z",
                "2023-01-01T00:00:00Z",
            ],
        },
    }

    if provider is not None:
        new_data = {}
        for machine_ in dummy_data:
            if provider in dummy_data[machine_]:
                new_data[machine_] = {provider: dummy_data[machine_][provider]}
        dummy_data = new_data

    if machine is None:
        return dummy_data
    else:
        return {machine: dummy_data[machine]}

def list_command(args: argparse.Namespace) -> None:
    if args.flake is None:
        raise ClanError("Could not find clan flake toplevel directory")
    backups = list_backups(Path(args.flake), machine=args.machine, provider=args.provider)
    if len(backups) > 0:
        pp = pprint.PrettyPrinter(depth=4)
        pp.pprint(backups)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--machine", type=str, help="machine in the flake to show backups of")
    parser.add_argument("--provider", type=str, help="backup provider to filter by")
    parser.set_defaults(func=list_command)
