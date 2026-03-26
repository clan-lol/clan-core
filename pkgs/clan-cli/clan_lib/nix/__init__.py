import json
import logging
import os
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

from clan_lib.cmd import run
from clan_lib.dirs import nixpkgs_source
from clan_lib.locked_open import locked_open

log = logging.getLogger(__name__)


def nix_command(flags: list[str], *, local: bool = True) -> list[str]:
    """Build a ``nix`` CLI invocation.

    Args:
        flags: Sub-command and its flags (e.g. ``["build", "--no-link", ...]``).
        local: Whether this command will run on the **local** machine.
            When *False*, host-specific options like ``--store`` (set via
            ``CLAN_TEST_STORE`` for the test suite) are omitted because
            they refer to local paths that don't exist on the remote.

    """
    args = [
        "nix",
        "--extra-experimental-features",
        "nix-command flakes",
        "--option",
        "warn-dirty",
        "false",
        *flags,
    ]
    # The test-store override is a local directory; only add it when the
    # command is executed on this machine.
    if local and (store := nix_test_store()):
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


def nix_build(
    flags: list[str],
    gcroot: Path | None = None,
    inputs_from: Path | None = None,
    *,
    local: bool = True,
) -> list[str]:
    """Build a ``nix build`` CLI invocation.

    Args:
        flags: Sub-command flags to append (e.g. the flake attribute).
        gcroot: If set, create a GC root symlink at this path.
        inputs_from: If set, use inputs from this flake path.
        local: Passed through to :func:`nix_command`; set to *False* when
            the build will run on a remote host.

    """
    return nix_command(
        [
            "build",
            "--flake-registry",
            "",
            "--print-out-paths",
            "--print-build-logs",
            *(["--inputs-from", str(inputs_from)] if inputs_from is not None else []),
            *(["--show-trace"] if log.isEnabledFor(logging.DEBUG) else []),
            *(["--out-link", str(gcroot)] if gcroot is not None else ["--no-link"]),
            *flags,
        ],
        local=local,
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
        fd, lock_nix = tempfile.mkstemp()
        os.close(fd)
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


# Re-export for backward compatibility
from clan_lib.nix.shell import Packages as Packages
from clan_lib.nix.shell import nix_shell as nix_shell
