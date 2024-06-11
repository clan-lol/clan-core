import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from clan_cli.errors import ClanError

from . import API


@dataclass
class FileFilter:
    title: str | None
    mime_types: list[str] | None
    patterns: list[str] | None
    suffixes: list[str] | None


@dataclass
class FileRequest:
    # Mode of the os dialog window
    mode: Literal["open_file", "select_folder", "save"]
    # Title of the os dialog window
    title: str | None = None
    # Pre-applied filters for the file dialog
    filters: FileFilter | None = None


@API.register
def open_file(file_request: FileRequest) -> str | None:
    """
    Abstract api method to open a file dialog window.
    It must return the name of the selected file or None if no file was selected.
    """
    raise NotImplementedError("Each specific platform should implement this function.")


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
