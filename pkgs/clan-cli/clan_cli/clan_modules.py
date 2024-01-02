import json
from pathlib import Path

from clan_cli.nix import nix_eval

from .cmd import run


def get_clan_module_names(
    flake_dir: Path,
) -> list[str]:
    """
    Get the list of clan modules from the clan-core flake input
    """
    proc = run(
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
        cwd=flake_dir,
    )

    module_names = json.loads(proc.stdout)
    return module_names
