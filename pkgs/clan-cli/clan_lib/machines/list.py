import logging
import re
from dataclasses import dataclass

from clan_cli.machines.hardware import HardwareConfig

from clan_lib.api import API
from clan_lib.dirs import specific_machine_dir
from clan_lib.flake import Flake
from clan_lib.machines.actions import get_machine, list_machines
from clan_lib.machines.machines import Machine
from clan_lib.nix_models.clan import InventoryMachine
from clan_lib.services.modules import parse_frontmatter
from clan_lib.templates.disk import MachineDiskMatter

log = logging.getLogger(__name__)


def instantiate_inventory_to_machines(
    flake: Flake, machines: dict[str, InventoryMachine]
) -> dict[str, Machine]:
    return {
        name: Machine.from_inventory(name, flake, _inventory_machine)
        for name, _inventory_machine in machines.items()
    }


def list_full_machines(flake: Flake) -> dict[str, Machine]:
    """
    Like `list_machines`, but returns a full 'machine' instance for each machine.
    """
    machines = list_machines(flake)

    return instantiate_inventory_to_machines(flake, machines)


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


# TODO: Remove this function
# Split out the disko schema extraction into a separate function
# get machine returns the machine already
@API.register
def get_machine_details(machine: Machine) -> MachineDetails:
    """Retrieve detailed information about a machine, including its inventory,
    hardware configuration, and disk schema if available.
    Args:
        machine (Machine): The machine instance for which details are to be retrieved.
    Returns:
        MachineDetails: An instance containing the machine's inventory, hardware configuration,
        and disk schema.
    Raises:
        ClanError: If the machine's inventory cannot be found or if there are issues with the
        hardware configuration or disk schema extraction.
    """
    machine_inv = get_machine(machine.flake, machine.name)
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
