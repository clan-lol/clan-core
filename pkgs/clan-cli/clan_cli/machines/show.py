import argparse
import dataclasses
import json
import logging
from pathlib import Path

from clan_cli.api import API

from ..cmd import run_no_stdout
from ..completions import add_dynamic_completer, complete_machines
from ..nix import nix_config, nix_eval
from .types import machine_name_type

log = logging.getLogger(__name__)


@dataclasses.dataclass
class MachineInfo:
    machine_name: str
    machine_description: str | None
    machine_icon: str | None


@API.register
def show_machine(flake_url: str | Path, machine_name: str) -> MachineInfo:
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{flake_url}#clanInternals.machines.{system}.{machine_name}",
            "--apply",
            "machine: { inherit (machine.config.clan.core) machineDescription machineIcon machineName; }",
            "--json",
        ]
    )
    proc = run_no_stdout(cmd)
    res = proc.stdout.strip()
    machine = json.loads(res)

    return MachineInfo(
        machine_name=machine.get("machineName"),
        machine_description=machine.get("machineDescription", None),
        machine_icon=machine.get("machineIcon", None),
    )


def show_command(args: argparse.Namespace) -> None:
    machine = show_machine(args.flake.path, args.machine)
    print(f"Name: {machine.machine_name}")
    print(f"Description: {machine.machine_description or ''}")
    print(f"Icon: {machine.machine_icon or ''}")


def register_show_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_command)
    machine_parser = parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    add_dynamic_completer(machine_parser, complete_machines)
