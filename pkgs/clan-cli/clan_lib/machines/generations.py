import json
from dataclasses import dataclass, field

from clan_lib.api import API
from clan_lib.ssh.localhost import LocalHost
from clan_lib.ssh.remote import Remote


@dataclass(order=True, frozen=True)
class MachineGeneration:
    generation: int
    date: str
    nixos_version: str
    kernel_version: str
    configuration_revision: str
    specialisations: list[str] = field(default_factory=list)
    current: bool = False


@API.register
def get_machine_generations(target_host: Remote | LocalHost) -> list[MachineGeneration]:
    """Get the nix generations installed on the target host and compare them with the machine."""
    with target_host.host_connection() as target_host_conn:
        cmd = [
            "nixos-rebuild",
            "list-generations",
            "--json",
        ]
        res = target_host_conn.run(cmd)

        data = json.loads(res.stdout.strip())
        sorted_data = sorted(data, key=lambda gen: gen.get("generation", 0))
        return [
            MachineGeneration(
                generation=gen.get("generation"),
                date=gen.get("date"),
                nixos_version=gen.get("nixosVersion", ""),
                kernel_version=gen.get("kernelVersion", ""),
                configuration_revision=gen.get("configurationRevision", ""),
                specialisations=gen.get("specialisations", []),
                current=gen.get("current", False),
            )
            for gen in sorted_data
        ]
