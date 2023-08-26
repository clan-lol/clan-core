import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from clan_cli.dirs import get_clan_flake_toplevel


def config_for_machine(machine_name: str, flake: Optional[Path] = None) -> dict:
    # find the flake root
    if flake is None:
        flake = get_clan_flake_toplevel()
    # read the config from a json file located at {flake}/machines/{machine_name}.json
    config_path = flake / "machines" / f"{machine_name}.json"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return json.load(f)


def set_config_for_machine(
    machine_name: str, config: dict, flake: Optional[Path] = None
) -> None:
    # find the flake root
    if flake is None:
        flake = get_clan_flake_toplevel()
    # write the config to a json file located at {flake}/machines/{machine_name}.json
    config_path = flake / "machines" / f"{machine_name}.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f)


def schema_for_machine(machine_name: str, flake: Optional[Path] = None) -> dict:
    if flake is None:
        flake = get_clan_flake_toplevel()
    # use nix eval to lib.evalModules .#clanModules.machine-{machine_name}
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
                lib = flake.inputs.nixpkgs.lib;
                module = builtins.trace (builtins.attrNames flake) flake.clanModules.machine-{machine_name};
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
