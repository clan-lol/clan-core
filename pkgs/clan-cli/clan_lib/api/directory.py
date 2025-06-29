import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError
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
    mode: Literal["open_file", "select_folder", "save", "open_multiple_files"]
    # Title of the os dialog window
    title: str | None = field(default=None)
    # Pre-applied filters for the file dialog
    filters: FileFilter | None = field(default=None)
    initial_file: str | None = field(default=None)
    initial_folder: str | None = field(default=None)


@API.register_abstract
def open_file(file_request: FileRequest) -> list[str] | None:
    """
    Abstract api method to open a file dialog window.
    It must return the name of the selected file or None if no file was selected.
    """
    msg = "open_file() is not implemented"
    raise NotImplementedError(msg)


@dataclass
class File:
    path: str
    file_type: Literal["file", "directory", "symlink"]


@dataclass
class Directory:
    path: str
    files: list[File] = field(default_factory=list)


@API.register
def get_directory(flake: Flake) -> Directory:
    curr_dir = flake.path
    directory = Directory(path=str(curr_dir))

    if not curr_dir.is_dir():
        msg = f"Path {curr_dir} is not a directory"
        raise ClanError(msg)

    with os.scandir(curr_dir.resolve()) as it:
        for entry in it:
            if entry.is_symlink():
                directory.files.append(
                    File(
                        path=str(curr_dir / Path(entry.name)),
                        file_type="symlink",
                    )
                )
            elif entry.is_file():
                directory.files.append(
                    File(
                        path=str(curr_dir / Path(entry.name)),
                        file_type="file",
                    )
                )

            elif entry.is_dir():
                directory.files.append(
                    File(
                        path=str(curr_dir / Path(entry.name)),
                        file_type="directory",
                    )
                )

    return directory


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
def show_block_devices() -> Blockdevices:
    """
    Api method to show local block devices.

    It must return a list of block devices.
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
