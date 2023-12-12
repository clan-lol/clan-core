import argparse
import json
import logging
import shlex
import subprocess
from pathlib import Path

from ..errors import ClanError
from ..nix import nix_config, nix_eval

log = logging.getLogger(__name__)


def list_machines(flake_dir: Path) -> list[str]:
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{flake_dir}#clanInternals.machines.{system}",
            "--apply",
            "builtins.attrNames",
            "--json",
        ]
    )
    proc = subprocess.run(cmd, text=True, capture_output=True)
    assert proc.stdout is not None
    if proc.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
exit code: {proc.returncode}
stdout:
{proc.stdout}
stderr:
{proc.stderr}
"""
        )
    res = proc.stdout.strip()
    return json.loads(res)


def list_command(args: argparse.Namespace) -> None:
    for machine in list_machines(Path(args.flake)):
        print(machine)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
