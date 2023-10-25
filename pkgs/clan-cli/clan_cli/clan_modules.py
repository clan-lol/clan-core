import json
import subprocess
from pathlib import Path
from typing import Optional

from clan_cli.dirs import get_clan_flake_toplevel
from clan_cli.nix import nix_eval


def get_clan_module_names(
    flake: Optional[Path] = None,
) -> tuple[list[str], Optional[str]]:
    """
    Get the list of clan modules from the clan-core flake input
    """
    if flake is None:
        flake = get_clan_flake_toplevel()
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
