from pathlib import Path

from ..dirs import get_clan_flake_toplevel


def machines_folder() -> Path:
    return get_clan_flake_toplevel() / "machines"


def machine_folder(machine: str) -> Path:
    return machines_folder() / machine
