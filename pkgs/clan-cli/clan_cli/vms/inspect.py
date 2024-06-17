import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from ..completions import add_dynamic_completer, complete_machines
from ..machines.machines import Machine


@dataclass
class VmConfig:
    machine_name: str
    machine_icon: Path
    machine_description: str
    flake_url: str | Path
    clan_name: str

    cores: int
    memory_size: int
    graphics: bool
    waypipe: bool = False


def inspect_vm(machine: Machine) -> VmConfig:
    data = json.loads(machine.eval_nix("config.clan.core.vm.inspect"))
    return VmConfig(flake_url=str(machine.flake), **data)


@dataclass
class InspectOptions:
    machine: str
    flake: Path


def inspect_command(args: argparse.Namespace) -> None:
    inspect_options = InspectOptions(
        machine=args.machine,
        flake=args.flake or Path.cwd(),
    )

    machine = Machine(inspect_options.machine, inspect_options.flake)
    res = inspect_vm(machine)
    print("Cores:", res.cores)
    print("Memory size:", res.memory_size)
    print("Graphics:", res.graphics)


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    machine_action = parser.add_argument("machine", type=str, default="defaultVM")
    add_dynamic_completer(machine_action, complete_machines)
    parser.set_defaults(func=inspect_command)
