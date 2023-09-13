import json
import os
import tempfile

from .dirs import get_clan_flake_toplevel, nixpkgs_flake, nixpkgs_source, unfree_nixpkgs


def nix_build_machine(machine: str, attr: list[str]) -> list[str]:
    clan_flake = get_clan_flake_toplevel()
    payload = json.dumps(
        dict(
            clan_flake=clan_flake,
            machine=machine,
            attr=attr,
        )
    )
    return [
        "nix",
        "build",
        "--impure",
        "--print-out-paths",
        "--expr",
        f'let args = builtins.fromJSON "{payload}"; in '
        """
          let
            flake = builtins.getFlake args.clan_flake;
            config = flake.nixosConfigurations.${args.machine}.extendModules {
              modules = [{
                clanCore.clanDir = args.clan_flake;
              }];
            };
          in
             flake.inputs.nixpkgs.lib.getAttrFromPath args.attr config
        """,
    ]


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
                str(nixpkgs_source()),
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
            f"{str(nixpkgs_flake())}",
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
