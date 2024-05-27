import json
from pathlib import Path

from ..cmd import run_no_stdout
from ..nix import nix_build, nix_config
from .machines import Machine


# function to speedup eval if we want to evauluate all machines
def get_all_machines(flake_dir: Path) -> list[Machine]:
    config = nix_config()
    system = config["system"]
    json_path = run_no_stdout(
        nix_build([f'{flake_dir}#clanInternals.all-machines-json."{system}"'])
    ).stdout

    machines_json = json.loads(Path(json_path.rstrip()).read_text())

    machines = []
    for name, machine_data in machines_json.items():
        machines.append(
            Machine(name=name, flake=flake_dir, deployment_info=machine_data)
        )
    return machines


def get_selected_machines(flake_dir: Path, machine_names: list[str]) -> list[Machine]:
    machines = []
    for name in machine_names:
        machines.append(Machine(name=name, flake=flake_dir))
    return machines
