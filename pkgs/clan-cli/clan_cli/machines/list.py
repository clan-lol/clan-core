import argparse
import json
import logging
from pathlib import Path

from clan_cli.api import API
from clan_cli.cmd import run_no_stdout
from clan_cli.errors import ClanError
from clan_cli.inventory import Machine, load_inventory_eval
from clan_cli.nix import nix_eval

log = logging.getLogger(__name__)


@API.register
def list_inventory_machines(flake_url: str | Path) -> dict[str, Machine]:
    inventory = load_inventory_eval(flake_url)
    return inventory.machines


@API.register
def list_nixos_machines(flake_url: str | Path) -> list[str]:
    cmd = nix_eval(
        [
            f"{flake_url}#nixosConfigurations",
            "--apply",
            "builtins.attrNames",
            "--json",
        ]
    )
    proc = run_no_stdout(cmd)

    try:
        res = proc.stdout.strip()
        data = json.loads(res)
        return data
    except json.JSONDecodeError as e:
        raise ClanError(f"Error decoding machines from flake: {e}")


def list_command(args: argparse.Namespace) -> None:
    flake_path = args.flake.path
    for name in list_nixos_machines(flake_path):
        print(name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
