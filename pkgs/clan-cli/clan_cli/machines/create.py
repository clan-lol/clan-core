import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clan_cli.api import API
from clan_cli.config.machine import set_config_for_machine

log = logging.getLogger(__name__)


@dataclass
class MachineCreateRequest:
    name: str
    config: dict[str, Any]


@API.register
def create_machine(flake_dir: str | Path, machine: MachineCreateRequest) -> None:
    set_config_for_machine(Path(flake_dir), machine.name, machine.config)


def create_command(args: argparse.Namespace) -> None:
    create_machine(args.flake, MachineCreateRequest(args.machine, dict()))


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=create_command)
