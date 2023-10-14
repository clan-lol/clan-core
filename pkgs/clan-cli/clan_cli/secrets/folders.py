import os
import shutil
from pathlib import Path
from typing import Callable

from ..dirs import specific_flake_dir
from ..errors import ClanError
from ..flakes.types import FlakeName


def get_sops_folder(flake_name: FlakeName) -> Path:
    return specific_flake_dir(flake_name) / "sops"


def gen_sops_subfolder(subdir: str) -> Callable[[FlakeName], Path]:
    def folder(flake_name: FlakeName) -> Path:
        return specific_flake_dir(flake_name) / "sops" / subdir

    return folder


sops_secrets_folder = gen_sops_subfolder("secrets")
sops_users_folder = gen_sops_subfolder("users")
sops_machines_folder = gen_sops_subfolder("machines")
sops_groups_folder = gen_sops_subfolder("groups")


def list_objects(path: Path, is_valid: Callable[[str], bool]) -> list[str]:
    objs: list[str] = []
    if not path.exists():
        return objs
    for f in os.listdir(path):
        if is_valid(f):
            objs.append(f)
    return objs


def remove_object(path: Path, name: str) -> None:
    try:
        shutil.rmtree(path / name)
    except FileNotFoundError:
        raise ClanError(f"{name} not found in {path}")
    if not os.listdir(path):
        os.rmdir(path)
