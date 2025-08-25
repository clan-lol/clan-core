import logging
import os
import sys
import urllib.parse
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from clan_lib.flake import Flake

log = logging.getLogger(__name__)


class MachineSpecProtocol(Protocol):
    @property
    def flake(self) -> "Flake": ...

    @property
    def name(self) -> str: ...


def get_clan_flake_toplevel_or_env() -> Path | None:
    if clan_dir := os.environ.get("CLAN_DIR"):
        return Path(clan_dir)
    return get_clan_flake_toplevel()


def get_clan_flake_toplevel() -> Path | None:
    try:
        return find_toplevel([".clan-flake", ".git", ".hg", ".svn", "flake.nix"])
    except OSError:
        # We might run clan from a directory that is not readable.
        return None


def clan_key_safe(flake_url: str) -> str:
    """Only embed the url in the path, not the clan name, as it would involve eval."""
    quoted_url = urllib.parse.quote_plus(flake_url)
    return f"{quoted_url}"


def find_toplevel(top_level_files: list[str]) -> Path | None:
    """Returns the path to the toplevel of the clan flake"""
    for project_file in top_level_files:
        initial_path = Path.cwd()
        path = Path(initial_path)
        while path.parent != path:
            if (path / project_file).exists():
                return path
            path = path.parent
    return None


def clan_core_flake() -> Path:
    """Returns the path to the clan core flake."""
    return module_root().parent.parent.parent


class TemplateType(Enum):
    CLAN = "clan"
    DISK = "disk"
    MACHINE = "machine"


def clan_templates(template_type: TemplateType | None = None) -> Path:
    template_path = module_root().parent.parent.parent / "templates"

    if template_type is not None:
        template_path /= template_type.value

    if template_path.exists():
        return template_path

    template_path = module_root() / "clan_core_templates"

    if template_type is not None:
        template_path /= template_type.value

    if not template_path.exists():
        msg = f"BUG! clan core not found at {template_path}. This is an issue with packaging the cli"
        raise ClanError(msg)

    return template_path


def user_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA", Path("~\\AppData\\Roaming\\").expanduser()))
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config)
    if sys.platform == "darwin":
        return Path("~/Library/Application Support/").expanduser()
    return Path("~/.config").expanduser()


def user_data_dir() -> Path:
    if sys.platform == "win32":
        return Path(
            Path(os.getenv("LOCALAPPDATA", Path("~\\AppData\\Local\\").expanduser())),
        )
    xdg_data = os.getenv("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data)
    if sys.platform == "darwin":
        return Path("~/Library/Application Support/").expanduser()
    return Path("~/.local/share").expanduser()


def user_cache_dir() -> Path:
    if sys.platform == "win32":
        return Path(
            Path(os.getenv("LOCALAPPDATA", Path("~\\AppData\\Local\\").expanduser())),
        )
    xdg_cache = os.getenv("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache)
    if sys.platform == "darwin":
        return Path("~/Library/Caches/").expanduser()
    return Path("~/.cache").expanduser()


def user_nixos_anywhere_dir() -> Path:
    p = user_config_dir() / "clan" / "nixos-anywhere"
    p.mkdir(parents=True, exist_ok=True)
    return p


def user_gcroot_dir() -> Path:
    p = user_config_dir() / "clan" / "gcroots"
    p.mkdir(parents=True, exist_ok=True)
    return p


def machine_gcroot(flake_url: str) -> Path:
    # Always build icon so that we can symlink it to the gcroot
    gcroot_dir = user_gcroot_dir()
    clan_gcroot = gcroot_dir / clan_key_safe(flake_url)
    clan_gcroot.mkdir(parents=True, exist_ok=True)
    return clan_gcroot


def user_history_file() -> Path:
    return user_config_dir() / "clan" / "history"


def vm_state_dir(flake_url: str, vm_name: str) -> Path:
    clan_key = clan_key_safe(str(flake_url))
    return user_data_dir() / "clan" / "vmstate" / clan_key / vm_name


def machines_dir(flake: "Flake") -> Path:
    if flake.is_local:
        return flake.path / "machines"

    store_path = flake.store_path
    if store_path is None:
        msg = "Invalid flake object. Doesn't have a store path"
        raise ClanError(msg)
    return Path(store_path) / "machines"


def specific_machine_dir(machine: "MachineSpecProtocol") -> Path:
    return machines_dir(machine.flake) / machine.name


def module_root() -> Path:
    return Path(__file__).parent.parent


def nixpkgs_flake() -> Path:
    return (module_root() / "nixpkgs").resolve()


def nixpkgs_source() -> Path:
    return (module_root() / "nixpkgs" / "path").resolve()


def select_source() -> Path:
    return (module_root() / "select").resolve()


def get_clan_directories(flake: "Flake") -> tuple[str, str]:
    """Get the clan source directory and computed clan directory paths.

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
    from clan_lib.nix import nix_eval

    # Get the source directory from nix store
    root_directory = flake.select("sourceInfo")

    # Get the configured directory using nix eval instead of flake.select
    # to avoid the select bug with clanInternals.inventoryClass.directory
    directory_result = run(
        nix_eval(
            flags=[
                f"{flake.identifier}#clanInternals.inventoryClass.directory",
            ],
        ),
    )
    directory = json.loads(directory_result.stdout.strip())

    # Both directories are in the nix store, but we need to calculate the relative path
    # to get the actual configured value (e.g., "./direct-config")
    root_path = Path(root_directory)
    directory_path = Path(directory)

    # No custom directory is set
    if root_path == directory_path:
        return (root_directory, "")

    try:
        relative_path = directory_path.relative_to(root_path)
        return (root_directory, str(relative_path))
    except ValueError as e:
        msg = (
            f"Directory path '{directory}' is not relative to root directory '{root_directory}'."
            "This indicates a configuration issue with the clan directory setting."
        )
        raise ClanError(msg) from e
