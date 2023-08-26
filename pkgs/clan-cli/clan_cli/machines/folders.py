from pathlib import Path

from ..dirs import get_clan_flake_toplevel


def machines_folder() -> Path:
    return get_clan_flake_toplevel() / "machines"


def machine_folder(machine: str) -> Path:
    return machines_folder() / machine


def machine_settings_file(machine: str) -> Path:
    return machine_folder(machine) / "settings.json"
