import argparse
import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from clan_lib.api import API
from clan_lib.api.disk import MachineDiskMatter
from clan_lib.api.modules import parse_frontmatter
from clan_lib.api.serde import dataclass_to_dict

from clan_cli.cmd import RunOpts, run
from clan_cli.completions import add_dynamic_completer, complete_tags
from clan_cli.dirs import specific_machine_dir
from clan_cli.errors import ClanError
from clan_cli.flake import Flake
from clan_cli.inventory import (
    load_inventory_eval,
    patch_inventory_with,
)
from clan_cli.inventory.classes import Machine as InventoryMachine
from clan_cli.machines.hardware import HardwareConfig
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_eval
from clan_cli.tags import list_nixos_machines_by_tags

log = logging.getLogger(__name__)


@API.register
def set_machine(flake: Flake, machine_name: str, machine: InventoryMachine) -> None:
    patch_inventory_with(flake, f"machines.{machine_name}", dataclass_to_dict(machine))


@API.register
def list_machines(flake: Flake) -> dict[str, InventoryMachine]:
    inventory = load_inventory_eval(flake)
    return inventory.get("machines", {})


@dataclass
class MachineDetails:
    machine: InventoryMachine
    hw_config: HardwareConfig | None = None
    disk_schema: MachineDiskMatter | None = None


def extract_header(c: str) -> str:
    header_lines = []
    for line in c.splitlines():
        match = re.match(r"^\s*#(.*)", line)
        if match:
            header_lines.append(match.group(1).strip())
        else:
            break  # Stop once the header ends
    return "\n".join(header_lines)


@API.register
def get_machine_details(machine: Machine) -> MachineDetails:
    inventory = load_inventory_eval(machine.flake)
    machine_inv = inventory.get("machines", {}).get(machine.name)
    if machine_inv is None:
        msg = f"Machine {machine.name} not found in inventory"
        raise ClanError(msg)

    hw_config = HardwareConfig.detect_type(machine)

    machine_dir = specific_machine_dir(machine)
    disk_schema: MachineDiskMatter | None = None
    disk_path = machine_dir / "disko.nix"
    if disk_path.exists():
        with disk_path.open() as f:
            content = f.read()
            header = extract_header(content)
            data, _rest = parse_frontmatter(header)
            if data:
                disk_schema = data  # type: ignore

    return MachineDetails(
        machine=machine_inv, hw_config=hw_config, disk_schema=disk_schema
    )


def list_nixos_machines(flake_url: str | Path) -> list[str]:
    cmd = nix_eval(
        [
            f"{flake_url}#clanInternals.machines.x86_64-linux",
            "--apply",
            "builtins.attrNames",
            "--json",
        ]
    )

    proc = run(cmd)

    try:
        res = proc.stdout.strip()
        data = json.loads(res)
    except json.JSONDecodeError as e:
        msg = f"Error decoding machines from flake: {e}"
        raise ClanError(msg) from e
    else:
        return data


@dataclass
class ConnectionOptions:
    timeout: int = 2
    retries: int = 10


from clan_cli.machines.machines import Machine


@API.register
def check_machine_online(
    machine: Machine, opts: ConnectionOptions | None = None
) -> Literal["Online", "Offline"]:
    hostname = machine.target_host_address
    if not hostname:
        msg = f"Machine {machine.name} does not specify a targetHost"
        raise ClanError(msg)

    timeout = opts.timeout if opts and opts.timeout else 2

    for _ in range(opts.retries if opts and opts.retries else 10):
        with machine.target_host() as target:
            res = target.run(
                ["true"],
                RunOpts(timeout=timeout, check=False, needs_user_terminal=True),
            )

            if res.returncode == 0:
                return "Online"
        time.sleep(timeout)

    return "Offline"


def list_command(args: argparse.Namespace) -> None:
    flake_path = args.flake.path
    if args.tags:
        list_nixos_machines_by_tags(flake_path, args.tags)
        return
    for name in list_nixos_machines(flake_path):
        print(name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    tag_parser = parser.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags that machines should be queried for. Multiple tags will intersect.",
    )
    add_dynamic_completer(tag_parser, complete_tags)
    parser.set_defaults(func=list_command)
