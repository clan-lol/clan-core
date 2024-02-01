import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from ..machines.machines import Machine


@dataclass
class VmConfig:
    machine_name: str
    flake_url: str | Path
    clan_name: str

    cores: int
    memory_size: int
    graphics: bool
    waypipe: bool = False


def inspect_vm(machine: Machine) -> VmConfig:
    data = json.loads(machine.eval_nix("config.clanCore.vm.inspect"))
    return VmConfig(machine_name=machine.name, flake_url=machine.flake, **data)


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
    parser.add_argument("machine", type=str, default="defaultVM")
    parser.set_defaults(func=inspect_command)
