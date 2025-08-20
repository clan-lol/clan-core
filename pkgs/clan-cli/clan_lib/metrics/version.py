import logging
from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.metrics.telegraf import get_metrics
from clan_lib.nix import nix_eval
from clan_lib.ssh.localhost import LocalHost
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class NixOSSystems:
    current_system: str
    booted_system: str
    current_kernel: str
    booted_kernel: str


def get_nixos_systems(
    machine: Machine, target_host: Remote | LocalHost
) -> NixOSSystems | None:
    """Get the nixos systems from the target host."""

    parsed_metrics = get_metrics(machine, target_host)

    for metric in parsed_metrics:
        if metric["name"] == "nixos_systems":
            return NixOSSystems(
                current_system=metric["tags"]["current_system"],
                booted_system=metric["tags"]["booted_system"],
                current_kernel=metric["tags"]["current_kernel"],
                booted_kernel=metric["tags"]["booted_kernel"],
            )
    return None


@API.register
def check_machine_up_to_date(
    machine: Machine,
    target_host: Remote | LocalHost,
) -> bool:
    """Check if a machine needs an update.
    Args:
        machine: The Machine instance to check.
        target_host: Optional Remote or LocalHost instance representing the target host.
    Returns:
        bool: True if the machine needs an update, False otherwise.
    """

    nixos_systems = get_nixos_systems(machine, target_host)

    if nixos_systems is None:
        msg = "Failed to find 'current_system_present' metric in telegraf logs."
        raise ClanError(msg)

    machine.info(f"Getting system outPath from {machine.name}...")

    git_out_path = nix_eval(
        [
            f"{machine.flake}#nixosConfigurations.'{machine.name}'.config.system.build.toplevel.outPath"
        ]
    )

    log.debug(
        f"Checking if {machine.name} needs an update:\n"
        f"Machine outPath: {nixos_systems.current_system}\n"
        f"Git outPath    : {git_out_path}\n"
    )

    return git_out_path != nixos_systems.current_system
