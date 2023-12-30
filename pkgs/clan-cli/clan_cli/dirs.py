import base64
import logging
import os
import sys
from pathlib import Path

log = logging.getLogger(__name__)


def get_clan_flake_toplevel() -> Path | None:
    return find_toplevel([".clan-flake", ".git", ".hg", ".svn", "flake.nix"])


def find_git_repo_root() -> Path | None:
    return find_toplevel([".git"])


def find_toplevel(top_level_files: list[str]) -> Path | None:
    """Returns the path to the toplevel of the clan flake"""
    for project_file in top_level_files:
        initial_path = Path(os.getcwd())
        path = Path(initial_path)
        while path.parent != path:
            if (path / project_file).exists():
                return path
            path = path.parent
    return None


def user_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming\\")))
    elif sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Application Support/"))
    else:
        return Path(os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")))


def user_gcroot_dir() -> Path:
    p = user_config_dir() / "clan" / "gcroots"
    p.mkdir(parents=True, exist_ok=True)
    return p


def specific_groot_dir(*, clan_name: str, flake_url: str) -> Path:
    # Always build icon so that we can symlink it to the gcroot
    gcroot_dir = user_gcroot_dir()
    burl = base64.urlsafe_b64encode(flake_url.encode()).decode()
    # Create the directory if it already exists append a number to it till it doesn't exist and then create it
    clan_gcroot = gcroot_dir / f"{clan_name}-{burl}"

    clan_gcroot.mkdir(parents=True, exist_ok=True)
    return clan_gcroot


def user_history_file() -> Path:
    return user_config_dir() / "clan" / "history"


def machines_dir(flake_dir: Path) -> Path:
    return flake_dir / "machines"


def specific_machine_dir(flake_dir: Path, machine: str) -> Path:
    return machines_dir(flake_dir) / machine


def machine_settings_file(flake_dir: Path, machine: str) -> Path:
    return specific_machine_dir(flake_dir, machine) / "settings.json"


def module_root() -> Path:
    return Path(__file__).parent


def nixpkgs_flake() -> Path:
    return (module_root() / "nixpkgs").resolve()


def nixpkgs_source() -> Path:
    return (module_root() / "nixpkgs" / "path").resolve()


def unfree_nixpkgs() -> Path:
    return module_root() / "nixpkgs" / "unfree"
