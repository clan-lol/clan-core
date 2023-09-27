import json
import os
import subprocess
import tempfile
from typing import Any

from .dirs import nixpkgs_flake, nixpkgs_source


def nix_command(flags: list[str]) -> list[str]:
    return ["nix", "--extra-experimental-features", "nix-command flakes"] + flags


def nix_build(
    flags: list[str],
) -> list[str]:
    return (
        nix_command(
            [
                "build",
                "--no-link",
                "--print-out-paths",
            ]
        )
        + flags
    )


def nix_config() -> dict[str, Any]:
    cmd = nix_command(["show-config", "--json"])
    proc = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
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
        ]
    )
    if os.environ.get("IN_NIX_SANDBOX"):
        with tempfile.TemporaryDirectory() as nix_store:
            return (
                default_flags
                + [
                    "--override-input",
                    "nixpkgs",
                    str(nixpkgs_source()),
                    # --store is required to prevent this error:
                    # error: cannot unlink '/nix/store/6xg259477c90a229xwmb53pdfkn6ig3g-default-builder.sh': Operation not permitted
                    "--store",
                    nix_store,
                ]
                + flags
            )
    return default_flags + flags


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    # we cannot use nix-shell inside the nix sandbox
    # in our tests we just make sure we have all the packages
    if os.environ.get("IN_NIX_SANDBOX"):
        return cmd
    wrapped_packages = [f"nixpkgs#{p}" for p in packages]
    return (
        nix_command(
            [
                "shell",
                "--inputs-from",
                f"{str(nixpkgs_flake())}",
            ]
        )
        + wrapped_packages
        + ["-c"]
        + cmd
    )
