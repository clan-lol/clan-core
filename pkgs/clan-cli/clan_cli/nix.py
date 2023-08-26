import os

from .dirs import flake_registry, unfree_nixpkgs


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
            "--flake-registry",
            str(flake_registry()),
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
