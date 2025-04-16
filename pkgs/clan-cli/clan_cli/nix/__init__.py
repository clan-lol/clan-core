import json
import logging
import os
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

from clan_cli.cmd import run, run_no_stdout
from clan_cli.dirs import nixpkgs_flake, nixpkgs_source
from clan_cli.errors import ClanError
from clan_cli.locked_open import locked_open

log = logging.getLogger(__name__)


def nix_command(flags: list[str]) -> list[str]:
    args = ["nix", "--extra-experimental-features", "nix-command flakes", *flags]
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
        ]
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
        ]
    )


def nix_add_to_gcroots(nix_path: Path, dest: Path) -> None:
    if not os.environ.get("IN_NIX_SANDBOX"):
        cmd = ["nix-store", "--realise", f"{nix_path}", "--add-root", f"{dest}"]
        run(cmd)


@cache
def nix_config() -> dict[str, Any]:
    cmd = nix_command(["config", "show", "--json"])
    proc = run_no_stdout(cmd)
    data = json.loads(proc.stdout)
    config = {}
    for key, value in data.items():
        config[key] = value["value"]
    return config


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
        ]
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
    data = json.loads(proc.stdout)
    return data


# Deprecated: use nix_shell() instead
def nix_shell_legacy(packages: list[str], cmd: list[str]) -> list[str]:
    # we cannot use nix-shell inside the nix sandbox
    # in our tests we just make sure we have all the packages
    if (
        os.environ.get("IN_NIX_SANDBOX")
        or os.environ.get("CLAN_NO_DYNAMIC_DEPS")
        or len(packages) == 0
    ):
        return cmd
    return [
        *nix_command(["shell", "--inputs-from", f"{nixpkgs_flake()!s}"]),
        *packages,
        "-c",
        *cmd,
    ]


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
        """
        Determines if a program is shipped with the clan package.
        """
        if cls.static_packages is None:
            cls.static_packages = set(
                os.environ.get("CLAN_PROVIDED_PACKAGES", "").split(":")
            )
        return program in cls.static_packages


# Alternative implementation of nix_shell() to replace nix_shell_legacy() at some point
#   Features:
#     - allow list for programs (need to be specified in allowed-packages.json)
#     - be abe to compute a closure of all deps for testing
#     - build clan distributions that ship some or all packages (eg. clan-cli-full)
def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    for program in packages:
        Packages.ensure_allowed(program)
    if os.environ.get("IN_NIX_SANDBOX"):
        return cmd
    missing_packages = [
        f"nixpkgs#{package}"
        for package in packages
        if not Packages.is_provided(package)
    ]
    if not missing_packages:
        return cmd
    return [
        *nix_command(["shell", "--inputs-from", f"{nixpkgs_flake()!s}"]),
        *missing_packages,
        "-c",
        *cmd,
    ]
