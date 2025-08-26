import json
import logging
import os
import shutil
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.locked_open import locked_open

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


def nix_add_to_gcroots(nix_path: Path, dest: Path) -> None:
    if not os.environ.get("IN_NIX_SANDBOX"):
        cmd = ["nix-store", "--realise", f"{nix_path}", "--add-root", f"{dest}"]
        run(cmd)


@cache
def nix_config() -> dict[str, Any]:
    cmd = nix_command(["config", "show", "--json"])
    proc = run(cmd)
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
        ],
    )
    if os.environ.get("IN_NIX_SANDBOX"):
        from clan_lib.dirs import nixpkgs_source  # noqa: PLC0415

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

        if "#" in package:
            log.warning(
                "Allowing package %s for debugging as it looks like a flakeref",
                package,
            )
            return

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

        if "#" in program:
            return True

        if program in cls.static_packages:
            if shutil.which(program) is None:
                log.warning(
                    "Program %s is not in the path even though it should be shipped with clan",
                    program,
                )
                return False
            return True
        return False


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
    ] + [package for package in packages if "#" in package]
    if not missing_packages:
        return cmd

    from clan_lib.dirs import nixpkgs_flake  # noqa: PLC0415

    return [
        *nix_command(["shell", "--inputs-from", f"{nixpkgs_flake()!s}"]),
        *missing_packages,
        "-c",
        *cmd,
    ]
