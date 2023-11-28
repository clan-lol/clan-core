import argparse
import pprint
from pathlib import Path
from typing import Optional

from ..errors import ClanError


def create_backup(flake_dir: Path, machine: Optional[str] = None, provider: Optional[str] = None) -> None:
    if machine is None:
        # TODO get all machines here
        machines = [ "machine1", "machine2" ]
    else:
        machines = [ machine ]

    if provider is None:
        # TODO get all providers here
        providers = [ "provider1", "provider2" ]
    else:
        providers = [ provider ]

    print("would create backups for machines: ", machines, " with providers: ", providers) 


def create_command(args: argparse.Namespace) -> None:
    if args.flake is None:
        raise ClanError("Could not find clan flake toplevel directory")
    create_backup(Path(args.flake), machine=args.machine, provider=args.provider)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--machine", type=str, help="machine in the flake to create backups of")
    parser.add_argument("--provider", type=str, help="backup provider to use")
    parser.set_defaults(func=create_command)
