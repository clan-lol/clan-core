import json
import os
import shutil
from pathlib import Path
from typing import Callable

from ..dirs import get_clan_flake_toplevel
from ..errors import ClanError


def get_sops_folder() -> Path:
    return get_clan_flake_toplevel() / "sops"


def gen_sops_subfolder(subdir: str) -> Callable[[], Path]:
    def folder() -> Path:
        return get_clan_flake_toplevel() / "sops" / subdir

    return folder


sops_secrets_folder = gen_sops_subfolder("secrets")
sops_users_folder = gen_sops_subfolder("users")
sops_machines_folder = gen_sops_subfolder("machines")
sops_groups_folder = gen_sops_subfolder("groups")


def list_objects(path: Path, is_valid: Callable[[str], bool]) -> None:
    if not path.exists():
        return
    for f in os.listdir(path):
        if is_valid(f):
            print(f)


def remove_object(path: Path, name: str) -> None:
    try:
        shutil.rmtree(path / name)
    except FileNotFoundError:
        raise ClanError(f"{name} not found in {path}")
    if not os.listdir(path):
        os.rmdir(path)


def add_key(path: Path, publickey: str, overwrite: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if not overwrite:
            flags |= os.O_EXCL
        fd = os.open(path / "key.json", flags)
    except FileExistsError:
        raise ClanError(f"{path.name} already exists in {path}")
    with os.fdopen(fd, "w") as f:
        json.dump({"publickey": publickey, "type": "age"}, f, indent=2)


def read_key(path: Path) -> str:
    with open(path / "key.json") as f:
        try:
            key = json.load(f)
        except json.JSONDecodeError as e:
            raise ClanError(f"Failed to decode {path.name}: {e}")
    if key["type"] != "age":
        raise ClanError(
            f"{path.name} is not an age key but {key['type']}. This is not supported"
        )
    publickey = key.get("publickey")
    if not publickey:
        raise ClanError(f"{path.name} does not contain a public key")
    return publickey
