import json
import subprocess
from pathlib import Path

from clan_cli.nix import nix_eval


def get_clan_module_names(
    flake_dir: Path,
) -> tuple[list[str], str | None]:
    """
    Get the list of clan modules from the clan-core flake input
    """
    proc = subprocess.run(
        nix_eval(
            [
                "--impure",
                "--show-trace",
                "--expr",
                f"""
        let
            flake = builtins.getFlake (toString {flake_dir});
        in
            builtins.attrNames flake.inputs.clan-core.clanModules
        """,
            ],
        ),
        capture_output=True,
        text=True,
        cwd=flake_dir,
    )
    if proc.returncode != 0:
        return [], proc.stderr
    module_names = json.loads(proc.stdout)
    return module_names, None
