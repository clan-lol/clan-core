import argparse
import logging
import re
from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.api.disk import MachineDiskMatter
from clan_lib.api.modules import parse_frontmatter
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.inventory import Machine as InventoryMachine
from clan_lib.persist.inventory_store import InventoryStore

from clan_cli.completions import add_dynamic_completer, complete_tags
from clan_cli.dirs import specific_machine_dir
from clan_cli.machines.hardware import HardwareConfig
from clan_cli.machines.inventory import get_machine
from clan_cli.machines.machines import Machine

log = logging.getLogger(__name__)


@API.register
def list_inv_machines(flake: Flake) -> dict[str, InventoryMachine]:
    """
    List machines in the inventory for the UI.
    """
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    res = inventory.get("machines", {})
    return res


def list_machines(
    flake: Flake, nix_options: list[str] | None = None
) -> dict[str, Machine]:
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()
    res = {}

    if nix_options is None:
        nix_options = []

    for inv_machine in inventory.get("machines", {}).values():
        name = inv_machine.get("name")
        # Technically, this should not happen, but we are defensive here.
        if name is None:
            msg = "InternalError: Machine name is required. But got a machine without a name."
            raise ClanError(msg)

        machine = Machine(
            name=name,
            flake=flake,
            nix_options=nix_options,
        )
        res[machine.name] = machine

    return res


def query_machines_by_tags(flake: Flake, tags: list[str]) -> dict[str, Machine]:
    """
    Query machines by their respective tags, if multiple tags are specified
    then only machines that have those respective tags specified will be listed.
    It is an intersection of the tags and machines.
    """
    machines = list_machines(flake)

    filtered_machines = {}
    for machine in machines.values():
        inv_machine = get_machine(machine)
        machine_tags = inv_machine.get("tags", [])
        if all(tag in machine_tags for tag in tags):
            filtered_machines[machine.name] = machine

    return filtered_machines


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
    machine_inv = get_machine(machine)
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
        machine=machine_inv,
        hw_config=hw_config,
        disk_schema=disk_schema,
    )


def list_command(args: argparse.Namespace) -> None:
    flake: Flake = args.flake

    if args.tags:
        for name in query_machines_by_tags(flake, args.tags):
            print(name)
    else:
        for name in list_machines(flake):
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
