import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from clan_cli.errors import ClanError

from . import API


@dataclass
class File:
    path: str
    file_type: Literal["file", "directory", "symlink"]


@dataclass
class Directory:
    path: str
    files: list[File] = field(default_factory=list)


@API.register
def get_directory(current_path: str) -> Directory:
    curr_dir = Path(current_path)
    directory = Directory(path=str(curr_dir))

    if not curr_dir.is_dir():
        raise ClanError()

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
