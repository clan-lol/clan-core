import argparse
import logging
from typing import Dict

from ..async_cmd import CmdOut, run, runforcli
from ..nix import nix_shell
from .folders import machine_folder

log = logging.getLogger(__name__)

async def create_machine(name: str) -> Dict[str, CmdOut]:
    folder = machine_folder(name)
    folder.mkdir(parents=True, exist_ok=True)

    # create empty settings.json file inside the folder
    with open(folder / "settings.json", "w") as f:
        f.write("{}")
    response = {}
    out = await run(nix_shell(["git"], ["git", "add", str(folder)]))
    response["git add"] = out

    out = await run(nix_shell(["git"], ["git", "commit", "-m", f"Added machine {name}", str(folder)]))
    response["git commit"] = out

    return response

def create_command(args: argparse.Namespace) -> None:
    runforcli(create_machine, args.host)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("host", type=str)
    parser.set_defaults(func=create_command)
