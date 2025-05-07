import logging
import urllib
from pathlib import Path

from clan_cli.flake import Flake

from .dirs import user_data_dir, user_gcroot_dir

log = logging.getLogger(__name__)


def clan_key_safe(flake_url: str) -> str:
    """
    only embed the url in the path, not the clan name, as it would involve eval.
    """
    quoted_url = urllib.parse.quote_plus(flake_url)
    return f"{quoted_url}"


def machine_gcroot(flake_url: str) -> Path:
    # Always build icon so that we can symlink it to the gcroot
    gcroot_dir = user_gcroot_dir()
    clan_gcroot = gcroot_dir / clan_key_safe(flake_url)
    clan_gcroot.mkdir(parents=True, exist_ok=True)
    return clan_gcroot


def vm_state_dir(flake_url: str, vm_name: str) -> Path:
    clan_key = clan_key_safe(str(flake_url))
    return user_data_dir() / "clan" / "vmstate" / clan_key / vm_name


def machines_dir(flake: Flake) -> Path:
    if flake.is_local:
        return flake.path / "machines"

    store_path = flake.store_path
    assert store_path is not None, "Invalid flake object"
    return Path(store_path) / "machines"


def specific_machine_dir(flake: Flake, machine: str) -> Path:
    return machines_dir(flake) / machine
