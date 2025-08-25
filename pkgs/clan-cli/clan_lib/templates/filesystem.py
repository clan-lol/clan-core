import shutil
from pathlib import Path

from clan_lib.flake import Flake
from clan_lib.nix import (
    nix_command,
    run,
)


def realize_nix_path(clan_dir: Flake, nix_path: str) -> None:
    """Downloads / realizes a nix path into the nix store"""
    if Path(nix_path).exists():
        return

    cmd = [
        "flake",
        "prefetch",
        "--inputs-from",
        clan_dir.identifier,
        "--option",
        "flake-registry",
        "",
        nix_path,
    ]

    run(nix_command(cmd))


def copy_from_nixstore(src: Path, dest: Path) -> None:
    """Copy a directory from the nix store to a destination path.
    Uses `cp -r` to recursively copy the directory.
    Ensures the destination directory is writable by the user.
    """
    shutil.copytree(src, dest, dirs_exist_ok=True, symlinks=True)
    run(
        ["chmod", "-R", "u+w", str(dest)],
    )  # Ensure the destination is writable by the user
