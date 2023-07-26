import os
import sys
from pathlib import Path


def get_clan_flake_toplevel() -> Path:
    """Returns the path to the toplevel of the clan flake"""
    initial_path = Path(os.getcwd())
    path = Path(initial_path)
    while path.parent == path:
        project_files = [".clan-flake"]
        for project_file in project_files:
            if (path / project_file).exists():
                return path
        path = path.parent
    return initial_path


def user_data_dir() -> Path:
    if sys.platform == "win32":
        raise NotImplementedError("Windows is not supported")
    elif sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Application Support/"))
    else:
        return Path(os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share")))
