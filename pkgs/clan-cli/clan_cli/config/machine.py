import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from clan_cli.dirs import get_clan_flake_toplevel, nixpkgs
from clan_cli.machines.folders import machine_folder, machine_settings_file


def config_for_machine(machine_name: str) -> dict:
    # read the config from a json file located at {flake}/machines/{machine_name}.json
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
    # write the config to a json file located at {flake}/machines/{machine_name}.json
    if not machine_folder(machine_name).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Machine {machine_name} not found. Create the machine first`",
        )
    settings_path = machine_settings_file(machine_name)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(config, f)


def schema_for_machine(machine_name: str, flake: Optional[Path] = None) -> dict:
    if flake is None:
        flake = get_clan_flake_toplevel()
    # use nix eval to lib.evalModules .#nixosModules.machine-{machine_name}
    proc = subprocess.run(
        [
            "nix",
            "eval",
            "--json",
            "--impure",
            "--show-trace",
            "--extra-experimental-features",
            "nix-command flakes",
            "--expr",
            f"""
            let
                flake = builtins.getFlake (toString {flake});
                lib = import {nixpkgs()}/lib;
                module = flake.nixosModules.machine-{machine_name};
                evaled = lib.evalModules {{
                    modules = [module];
                }};
                clanOptions = evaled.options.clan;
                jsonschemaLib = import {Path(__file__).parent / "jsonschema"} {{ inherit lib; }};
                jsonschema = jsonschemaLib.parseOptions clanOptions;
            in
                jsonschema
            """,
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise Exception(
            f"Failed to read schema for machine {machine_name}:\n{proc.stderr}"
        )
    return json.loads(proc.stdout)
