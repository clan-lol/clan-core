import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..dirs import get_clan_flake_toplevel


def schema_for_machine(machine_name: str, flake: Optional[Path] = None) -> dict:
    if flake is None:
        flake = get_clan_flake_toplevel()
    # use nix eval to read from .#clanModules.<module_name>.options
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
