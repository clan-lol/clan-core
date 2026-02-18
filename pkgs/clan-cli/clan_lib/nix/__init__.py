import json
import logging
import os
import shutil
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

from clan_lib.cmd import run
from clan_lib.dirs import nixpkgs_source
from clan_lib.errors import ClanError
from clan_lib.locked_open import locked_open

log = logging.getLogger(__name__)


def nix_command(flags: list[str]) -> list[str]:
    args = [
        "nix",
        "--extra-experimental-features",
        "nix-command flakes",
        "--option",
        "warn-dirty",
        "false",
        *flags,
    ]
    if store := nix_test_store():
        args += ["--store", str(store)]
    return args


def nix_flake_show(flake_url: str | Path) -> list[str]:
    return nix_command(
        [
            "flake",
            "show",
            "--json",
            *(["--show-trace"] if log.isEnabledFor(logging.DEBUG) else []),
            str(flake_url),
        ],
    )


def nix_build(flags: list[str], gcroot: Path | None = None) -> list[str]:
    return nix_command(
        [
            "build",
            "--print-out-paths",
            "--print-build-logs",
            *(["--show-trace"] if log.isEnabledFor(logging.DEBUG) else []),
            *(["--out-root", str(gcroot)] if gcroot is not None else ["--no-link"]),
            *flags,
        ],
    )


@cache
def nix_config() -> dict[str, Any]:
    cmd = nix_command(["config", "show", "--json"])
    proc = run(cmd)
    data = json.loads(proc.stdout)
    config = {}
    for key, value in data.items():
        config[key] = value["value"]
    return config


def current_system() -> str:
    """The (nix) system of the machine where this code is executed"""
    config = nix_config()
    return config["system"]


def nix_test_store() -> Path | None:
    store = os.environ.get("CLAN_TEST_STORE", None)
    lock_nix = os.environ.get("LOCK_NIX", "")

    if not lock_nix:
        lock_nix = tempfile.NamedTemporaryFile().name  # NOQA: SIM115
    if not os.environ.get("IN_NIX_SANDBOX"):
        return None
    if store:
        Path.mkdir(Path(store), exist_ok=True)
        with locked_open(Path(lock_nix), "w"):
            return Path(store)
    return None


def nix_eval(flags: list[str]) -> list[str]:
    default_flags = nix_command(
        [
            "eval",
            *(["--show-trace"] if log.isEnabledFor(logging.DEBUG) else []),
            "--json",
            "--print-build-logs",
        ],
    )
    if os.environ.get("IN_NIX_SANDBOX"):
        return [
            *default_flags,
            "--override-input",
            "nixpkgs",
            str(nixpkgs_source()),
            *flags,
        ]
    return default_flags + flags


def nix_metadata(flake_url: str | Path) -> dict[str, Any]:
    cmd = nix_command(["flake", "metadata", "--json", f"{flake_url}"])
    proc = run(cmd)
    return json.loads(proc.stdout)


# lazy loads list of allowed and static programs
class Packages:
    allowed_packages: set[str] | None = None
    static_packages: set[str] | None = None

    @classmethod
    def ensure_allowed(cls: type["Packages"], package: str) -> None:
        if cls.allowed_packages is None:
            with (Path(__file__).parent / "allowed-packages.json").open() as f:
                cls.allowed_packages = allowed_packages = set(json.load(f))
        else:
            allowed_packages = cls.allowed_packages

        if package not in allowed_packages:
            msg = f"Package not allowed: '{package}', allowed packages are:\n{'\n'.join(allowed_packages)}"
            raise ClanError(msg)

    @classmethod
    def is_provided(cls: type["Packages"], program: str) -> bool:
        """Determines if a program is shipped with the clan package."""
        if cls.static_packages is None:
            cls.static_packages = set(
                os.environ.get("CLAN_PROVIDED_PACKAGES", "").split(":"),
            )

        if program in cls.static_packages:
            if shutil.which(program) is None:
                log.warning(
                    "Program %s is not in the path even though it should be shipped with clan",
                    program,
                )
                return False
            return True
        return False


# Import after Packages and nix_command are defined to avoid circular import
from clan_lib.nix.shell import nix_shell

__all__ = ["nix_shell"]
