import json
import subprocess
from typing import Optional

from clan_cli.nix import nix_eval

from .dirs import specific_flake_dir
from .types import FlakeName


def get_clan_module_names(
    flake_name: FlakeName,
) -> tuple[list[str], Optional[str]]:
    """
    Get the list of clan modules from the clan-core flake input
    """
    flake = specific_flake_dir(flake_name)
    proc = subprocess.run(
        nix_eval(
            [
                "--impure",
                "--show-trace",
                "--expr",
                f"""
        let
            flake = builtins.getFlake (toString {flake});
        in
            builtins.attrNames flake.inputs.clan-core.clanModules
        """,
            ],
        ),
        capture_output=True,
        text=True,
        cwd=flake,
    )
    if proc.returncode != 0:
        return [], proc.stderr
    module_names = json.loads(proc.stdout)
    return module_names, None
