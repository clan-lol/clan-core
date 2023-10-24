import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from clan_cli.dirs import get_clan_flake_toplevel, nixpkgs_source
from clan_cli.git import commit_file, find_git_repo_root
from clan_cli.machines.folders import machine_folder, machine_settings_file
from clan_cli.nix import nix_eval


def verify_machine_config(
    machine_name: str, flake: Optional[Path] = None
) -> tuple[bool, Optional[str]]:
    """
    Verify that the machine evaluates successfully
    Returns a tuple of (success, error_message)
    """
    if flake is None:
        flake = get_clan_flake_toplevel()
    proc = subprocess.run(
        nix_eval(
            flags=[
                "--impure",
                "--show-trace",
                f".#nixosConfigurations.{machine_name}.config.system.build.toplevel.outPath",
            ],
        ),
        capture_output=True,
        text=True,
        cwd=flake,
    )
    if proc.returncode != 0:
        return False, proc.stderr
    return True, None


def config_for_machine(machine_name: str) -> dict:
    # read the config from a json file located at {flake}/machines/{machine_name}/settings.json
    if not machine_folder(machine_name).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Machine {machine_name} not found. Create the machine first`",
        )
    settings_path = machine_settings_file(machine_name)
    if not settings_path.exists():
        return {}
    with open(settings_path) as f:
        return json.load(f)


def set_config_for_machine(machine_name: str, config: dict) -> None:
    # write the config to a json file located at {flake}/machines/{machine_name}/settings.json
    if not machine_folder(machine_name).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Machine {machine_name} not found. Create the machine first`",
        )
    settings_path = machine_settings_file(machine_name)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(config, f)
    repo_dir = find_git_repo_root()

    if repo_dir is not None:
        commit_file(settings_path, repo_dir)


def schema_for_machine(machine_name: str, flake: Optional[Path] = None) -> dict:
    if flake is None:
        flake = get_clan_flake_toplevel()
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
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise Exception(
            f"Failed to read schema for machine {machine_name}:\n{proc.stderr}"
        )
    return json.loads(proc.stdout)
