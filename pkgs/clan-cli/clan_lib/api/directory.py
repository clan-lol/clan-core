import json
from dataclasses import dataclass, field
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
    """
    Api method to open a file dialog window.

    Implementations is specific to the platform and
    returns the name of the selected file or None if no file was selected.
    """
    msg = "get_system_file() is not implemented"
    raise NotImplementedError(msg)


@API.register_abstract
def get_clan_folder() -> Flake:
    """
    Api method to open the clan folder.

    Implementations is specific to the platform and returns the path to the clan folder.
    """
    msg = "get_clan_folder() is not implemented"
    raise NotImplementedError(msg)


@API.register
def get_clan_directories(flake: Flake) -> tuple[str, str]:
    """
    Get the clan source directory and computed clan directory paths.

    Args:
        flake: The clan flake to get directories from

    Returns:
        A tuple of (source_directory, computed_clan_directory) where:
        - source_directory: Path to the clan source in the nixpkgs store
        - computed_clan_directory: Computed clan directory path (source + relative directory)

    Raises:
        ClanError: If the flake evaluation fails or directories cannot be found
    """
    import json
    from pathlib import Path

    from clan_lib.cmd import run
    from clan_lib.errors import ClanError
    from clan_lib.nix import nix_eval

    # Get the source directory from nix store
    root_directory = flake.select("sourceInfo")

    # Get the configured directory using nix eval instead of flake.select
    # to avoid the select bug with clanInternals.inventoryClass.directory
    directory_result = run(
        nix_eval(
            flags=[
                f"{flake.identifier}#clanInternals.inventoryClass.directory",
            ]
        )
    )
    directory = json.loads(directory_result.stdout.strip())

    # Both directories are in the nix store, but we need to calculate the relative path
    # to get the actual configured value (e.g., "./direct-config")
    root_path = Path(root_directory)
    directory_path = Path(directory)

    try:
        relative_path = directory_path.relative_to(root_path)
        return (root_directory, str(relative_path))
    except ValueError as e:
        msg = f"Directory path '{directory}' is not relative to root directory '{root_directory}'. This indicates a configuration issue with the clan directory setting."
        raise ClanError(msg) from e


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
    """
    List local block devices by running `lsblk`.

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
        blockdevices=[blk_from_dict(device) for device in blk_info["blockdevices"]]
    )


@API.register
def get_clan_directory_relative(flake: Flake) -> str:
    """
    Get the clan directory path relative to the flake root
    from the clan.directory configuration setting.

    Args:
        flake: The clan flake to get the relative directory from

    Returns:
        The relative directory path (e.g., ".", "direct-config", "subdir/config")

    Raises:
        ClanError: If the flake evaluation fails or directories cannot be found
    """
    _, relative_dir = get_clan_directories(flake)
    return relative_dir
