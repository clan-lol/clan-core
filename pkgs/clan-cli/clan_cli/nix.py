import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .cmd import run
from .dirs import nixpkgs_flake, nixpkgs_source


def nix_command(flags: list[str]) -> list[str]:
    return ["nix", "--extra-experimental-features", "nix-command flakes", *flags]


def nix_flake_show(flake_url: str | Path) -> list[str]:
    return nix_command(
        [
            "flake",
            "show",
            "--json",
            "--show-trace",
            "--no-write-lock-file",
            f"{flake_url}",
        ]
    )


def nix_build(flags: list[str], gcroot: Path | None = None) -> list[str]:
    if gcroot is not None:
        return (
            nix_command(
                [
                    "build",
                    "--out-link",
                    str(gcroot),
                    "--print-out-paths",
                    "--no-write-lock-file",
                ]
            )
            + flags
        )
    else:
        return (
            nix_command(
                [
                    "build",
                    "--no-link",
                    "--print-out-paths",
                    "--no-write-lock-file",
                ]
            )
            + flags
        )


def nix_add_to_gcroots(nix_path: Path, dest: Path) -> None:
    cmd = ["nix-store", "--realise", f"{nix_path}", "--add-root", f"{dest}"]
    run(cmd)


def nix_config() -> dict[str, Any]:
    cmd = nix_command(["config", "show", "--json"])
    proc = run(cmd)
    data = json.loads(proc.stdout)
    config = {}
    for key, value in data.items():
        config[key] = value["value"]
    return config


def nix_eval(flags: list[str]) -> list[str]:
    default_flags = nix_command(
        [
            "eval",
            "--show-trace",
            "--json",
            "--no-write-lock-file",
        ]
    )
    if os.environ.get("IN_NIX_SANDBOX"):
        with tempfile.TemporaryDirectory() as nix_store:
            return [
                *default_flags,
                "--override-input",
                "nixpkgs",
                str(nixpkgs_source()),
                # --store is required to prevent this error:
                # error: cannot unlink '/nix/store/6xg259477c90a229xwmb53pdfkn6ig3g-default-builder.sh': Operation not permitted
                "--store",
                nix_store,
                *flags,
            ]
    return default_flags + flags


def nix_metadata(flake_url: str | Path) -> dict[str, Any]:
    cmd = nix_command(["flake", "metadata", "--json", f"{flake_url}"])
    proc = run(cmd)
    data = json.loads(proc.stdout)
    return data


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    # we cannot use nix-shell inside the nix sandbox
    # in our tests we just make sure we have all the packages
    if os.environ.get("IN_NIX_SANDBOX"):
        return cmd
    return [
        *nix_command(["shell", "--inputs-from", f"{nixpkgs_flake()!s}"]),
        *packages,
        "-c",
        *cmd,
    ]
