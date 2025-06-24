import logging
import re
from dataclasses import dataclass

from clan_cli.machines.hardware import HardwareConfig

from clan_lib.api import API
from clan_lib.api.disk import MachineDiskMatter
from clan_lib.api.modules import parse_frontmatter
from clan_lib.dirs import specific_machine_dir
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import get_machine, list_machines
from clan_lib.machines.machines import Machine
from clan_lib.nix_models.clan import InventoryMachine

log = logging.getLogger(__name__)


def list_full_machines(flake: Flake) -> dict[str, Machine]:
    """
    Like `list_machines`, but returns a full 'machine' instance for each machine.
    """
    machines = list_machines(flake)

    res: dict[str, Machine] = {}

    for inv_machine in machines.values():
        name = inv_machine.get("name")
        # Technically, this should not happen, but we are defensive here.
        if name is None:
            msg = "InternalError: Machine name is required. But got a machine without a name."
            raise ClanError(msg)

        machine = Machine(name=name, flake=flake)
        res[machine.name] = machine

    return res


def query_machines_by_tags(flake: Flake, tags: list[str]) -> dict[str, Machine]:
    """
    Query machines by their respective tags, if multiple tags are specified
    then only machines that have those respective tags specified will be listed.
    It is an intersection of the tags and machines.
    """
    machines = list_full_machines(flake)

    filtered_machines = {}
    for machine in machines.values():
        inv_machine = get_machine(machine.flake, machine.name)
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
