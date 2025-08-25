import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from clan_lib.cmd import RunOpts, run
from clan_lib.flake import Flake
from clan_lib.nix import nix_shell

from . import API


@dataclass
class FileFilter:
    title: str | None = field(default=None)
    mime_types: list[str] | None = field(default=None)
    patterns: list[str] | None = field(default=None)
    suffixes: list[str] | None = field(default=None)


@dataclass
class FileRequest:
    # Mode of the os dialog window
    mode: Literal["get_system_file", "select_folder", "save", "open_multiple_files"]
    # Title of the os dialog window
    title: str | None = field(default=None)
    # Pre-applied filters for the file dialog
    filters: FileFilter | None = field(default=None)
    initial_file: str | None = field(default=None)
    initial_folder: str | None = field(default=None)


@API.register_abstract
def get_system_file(file_request: FileRequest) -> list[str] | None:
    """Api method to open a file dialog window.

    Implementations is specific to the platform and
    returns the name of the selected file or None if no file was selected.
    """
    msg = "get_system_file() is not implemented"
    raise NotImplementedError(msg)


@API.register_abstract
def get_clan_folder() -> Flake:
    """Api method to open the clan folder.

    Implementations is specific to the platform and returns the path to the clan folder.
    """
    msg = "get_clan_folder() is not implemented"
    raise NotImplementedError(msg)


@dataclass
class BlkInfo:
    name: str
    id_link: str
    path: str
    rm: str
    size: str
    ro: bool
    mountpoints: list[str]
    type_: Literal["disk"]


@dataclass
class Blockdevices:
    blockdevices: list[BlkInfo]


def blk_from_dict(data: dict) -> BlkInfo:
    return BlkInfo(
        name=data["name"],
        path=data["path"],
        rm=data["rm"],
        size=data["size"],
        ro=data["ro"],
        mountpoints=data["mountpoints"],
        type_=data["type"],  # renamed
        id_link=data["id-link"],  # renamed
    )


@API.register
def list_system_storage_devices() -> Blockdevices:
    """List local block devices by running `lsblk`.

    Returns:
        A list of detected block devices with metadata like size, path, type, etc.

    """
    cmd = nix_shell(
        ["util-linux"],
        [
            "lsblk",
            "--json",
            "--output",
            "PATH,NAME,RM,SIZE,RO,MOUNTPOINTS,TYPE,ID-LINK",
        ],
    )
    proc = run(cmd, RunOpts(needs_user_terminal=True))
    res = proc.stdout.strip()

    blk_info: dict[str, Any] = json.loads(res)

    return Blockdevices(
        blockdevices=[blk_from_dict(device) for device in blk_info["blockdevices"]],
    )


@API.register
def get_clan_directory_relative(flake: Flake) -> str:
    """Get the clan directory path relative to the flake root
    from the clan.directory configuration setting.

    Args:
        flake: The clan flake to get the relative directory from

    Returns:
        The relative directory path (e.g., ".", "direct-config", "subdir/config")

    Raises:
        ClanError: If the flake evaluation fails or directories cannot be found

    """
    from clan_lib.dirs import get_clan_directories

    _, relative_dir = get_clan_directories(flake)
    return relative_dir


def get_clan_dir(flake: Flake) -> Path:
    """Get the effective clan directory, respecting the clan.directory configuration.

    Args:
        flake: The clan flake
    Returns:
        Path to the effective clan directory

    """
    relative_clan_dir = get_clan_directory_relative(flake)
    return flake.path / relative_clan_dir if relative_clan_dir else flake.path
