import argparse
import logging
from typing import Dict

from ..async_cmd import CmdOut, run, runforcli
from ..dirs import get_flake_path, specific_machine_dir
from ..errors import ClanError
from ..nix import nix_shell

log = logging.getLogger(__name__)


async def create_machine(flake_name: str, machine_name: str) -> Dict[str, CmdOut]:
    folder = specific_machine_dir(flake_name, machine_name)
    folder.mkdir(parents=True, exist_ok=True)

    # create empty settings.json file inside the folder
    with open(folder / "settings.json", "w") as f:
        f.write("{}")
    response = {}
    out = await run(nix_shell(["git"], ["git", "add", str(folder)]), cwd=folder)
    response["git add"] = out

    out = await run(
        nix_shell(
            ["git"],
            ["git", "commit", "-m", f"Added machine {machine_name}", str(folder)],
        ),
        cwd=folder,
    )
    response["git commit"] = out

    return response


def create_command(args: argparse.Namespace) -> None:
    try:
        flake_dir = get_flake_path(args.flake)
        runforcli(create_machine, flake_dir, args.machine)
    except ClanError as e:
        print(e)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=create_command)
