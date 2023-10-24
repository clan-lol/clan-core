import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import HTTPException

from clan_cli.dirs import (
    get_flake_path,
    machine_settings_file,
    nixpkgs_source,
    specific_machine_dir,
)
from clan_cli.git import commit_file, find_git_repo_root
from clan_cli.nix import nix_eval


def verify_machine_config(
    machine_name: str, config: Optional[dict] = None, flake: Optional[Path] = None
) -> Optional[str]:
    """
    Verify that the machine evaluates successfully
    Returns a tuple of (success, error_message)
    """
    if config is None:
        config = config_for_machine(machine_name)
    if flake is None:
        flake = get_clan_flake_toplevel()
    with NamedTemporaryFile(mode="w") as clan_machine_settings_file:
        json.dump(config, clan_machine_settings_file, indent=2)
        clan_machine_settings_file.seek(0)
        env = os.environ.copy()
        env["CLAN_MACHINE_SETTINGS_FILE"] = clan_machine_settings_file.name
        proc = subprocess.run(
            nix_eval(
                flags=[
                    "--impure",
                    "--show-trace",
                    "--show-trace",
                    "--impure",  # needed to access CLAN_MACHINE_SETTINGS_FILE
                    f".#nixosConfigurations.{machine_name}.config.system.build.toplevel.outPath",
                ],
            ),
            capture_output=True,
            text=True,
            cwd=flake,
            env=env,
        )
    if proc.returncode != 0:
        return proc.stderr
    return None


def config_for_machine(machine_name: str) -> dict:
    # read the config from a json file located at {flake}/machines/{machine_name}/settings.json
    if not specific_machine_dir(flake_name, machine_name).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Machine {machine_name} not found. Create the machine first`",
        )
    settings_path = machine_settings_file(flake_name, machine_name)
    if not settings_path.exists():
        return {}
    with open(settings_path) as f:
        return json.load(f)


def set_config_for_machine(flake_name: str, machine_name: str, config: dict) -> None:
    # write the config to a json file located at {flake}/machines/{machine_name}/settings.json
    if not specific_machine_dir(flake_name, machine_name).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Machine {machine_name} not found. Create the machine first`",
        )
    settings_path = machine_settings_file(flake_name, machine_name)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(config, f)
    repo_dir = find_git_repo_root()

    if repo_dir is not None:
        commit_file(settings_path, repo_dir)


def schema_for_machine(flake_name: str, machine_name: str) -> dict:
    flake = get_flake_path(flake_name)

    # use nix eval to lib.evalModules .#nixosModules.machine-{machine_name}
    proc = subprocess.run(
        nix_eval(
            flags=[
                "--impure",
                "--show-trace",
                "--expr",
                f"""
                let
                    flake = builtins.getFlake (toString {flake});
                    lib = import {nixpkgs_source()}/lib;
                    options = flake.nixosConfigurations.{machine_name}.options;
                    clanOptions = options.clan;
                    jsonschemaLib = import {Path(__file__).parent / "jsonschema"} {{ inherit lib; }};
                    jsonschema = jsonschemaLib.parseOptions clanOptions;
                in
                    jsonschema
                """,
            ],
        ),
        capture_output=True,
        text=True,
    )
# def schema_for_machine(
#     machine_name: str, config: Optional[dict] = None, flake: Optional[Path] = None
# ) -> dict:
#     if flake is None:
#         flake = get_clan_flake_toplevel()
#     # use nix eval to lib.evalModules .#nixosConfigurations.<machine_name>.options.clan
#     with NamedTemporaryFile(mode="w") as clan_machine_settings_file:
#         env = os.environ.copy()
#         inject_config_flags = []
#         if config is not None:
#             json.dump(config, clan_machine_settings_file, indent=2)
#             clan_machine_settings_file.seek(0)
#             env["CLAN_MACHINE_SETTINGS_FILE"] = clan_machine_settings_file.name
#             inject_config_flags = [
#                 "--impure",  # needed to access CLAN_MACHINE_SETTINGS_FILE
#             ]
#         proc = subprocess.run(
#             nix_eval(
#                 flags=inject_config_flags
#                 + [
#                     "--impure",
#                     "--show-trace",
#                     "--expr",
#                     f"""
#                     let
#                         flake = builtins.getFlake (toString {flake});
#                         lib = import {nixpkgs_source()}/lib;
#                         options = flake.nixosConfigurations.{machine_name}.options;
#                         clanOptions = options.clan;
#                         jsonschemaLib = import {Path(__file__).parent / "jsonschema"} {{ inherit lib; }};
#                         jsonschema = jsonschemaLib.parseOptions clanOptions;
#                     in
#                         jsonschema
#                     """,
#                 ],
#             ),
#             capture_output=True,
#             text=True,
#             cwd=flake,
#             env=env,
#         )
#     if proc.returncode != 0:
#         print(proc.stderr, file=sys.stderr)
#         raise Exception(
#             f"Failed to read schema for machine {machine_name}:\n{proc.stderr}"
#         )
#     return json.loads(proc.stdout)
