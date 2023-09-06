import os
import tempfile

from .dirs import deps_flake, nixpkgs, unfree_nixpkgs


def nix_eval(flags: list[str]) -> list[str]:
    if os.environ.get("IN_NIX_SANDBOX"):
        with tempfile.TemporaryDirectory() as nix_store:
            return [
                "nix",
                "eval",
                "--show-trace",
                "--extra-experimental-features",
                "nix-command flakes",
                "--override-input",
                "nixpkgs",
                str(nixpkgs()),
                # --store is required to prevent this error:
                # error: cannot unlink '/nix/store/6xg259477c90a229xwmb53pdfkn6ig3g-default-builder.sh': Operation not permitted
                "--store",
                nix_store,
            ] + flags
    return [
        "nix",
        "eval",
        "--show-trace",
        "--extra-experimental-features",
        "nix-command flakes",
    ] + flags


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    # we cannot use nix-shell inside the nix sandbox
    # in our tests we just make sure we have all the packages
    if os.environ.get("IN_NIX_SANDBOX"):
        return cmd
    wrapped_packages = [f"nixpkgs#{p}" for p in packages]
    return (
        [
            "nix",
            "shell",
            "--extra-experimental-features",
            "nix-command flakes",
            "--inputs-from",
            f"{str(deps_flake())}",
        ]
        + wrapped_packages
        + ["-c"]
        + cmd
    )


def unfree_nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    if os.environ.get("IN_NIX_SANDBOX"):
        return cmd
    return (
        [
            "nix",
            "shell",
            "--extra-experimental-features",
            "nix-command flakes",
            "-f",
            str(unfree_nixpkgs()),
        ]
        + packages
        + ["-c"]
        + cmd
    )
