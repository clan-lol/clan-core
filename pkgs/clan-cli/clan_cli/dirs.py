import os
import sys
from pathlib import Path
from typing import Optional

from .errors import ClanError


def get_clan_flake_toplevel() -> Path:
    return find_toplevel([".clan-flake", ".git", ".hg", ".svn", "flake.nix"])


def find_git_repo_root() -> Optional[Path]:
    try:
        return find_toplevel([".git"])
    except ClanError:
        return None


def find_toplevel(top_level_files: list[str]) -> Path:
    """Returns the path to the toplevel of the clan flake"""
    for project_file in top_level_files:
        initial_path = Path(os.getcwd())
        path = Path(initial_path)
        while path.parent != path:
            if (path / project_file).exists():
                return path
            path = path.parent
    raise ClanError("Could not find clan flake toplevel directory")


def user_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming\\")))
    elif sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Application Support/"))
    else:
        return Path(os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")))


def module_root() -> Path:
    return Path(__file__).parent


def nixpkgs_flake() -> Path:
    return (module_root() / "nixpkgs").resolve()


def nixpkgs_source() -> Path:
    return (module_root() / "nixpkgs" / "path").resolve()


def unfree_nixpkgs() -> Path:
    return module_root() / "nixpkgs" / "unfree"
