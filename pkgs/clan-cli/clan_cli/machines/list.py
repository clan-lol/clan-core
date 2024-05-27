import argparse
import dataclasses
import json
import logging
from pathlib import Path

from clan_cli.api import API

from ..cmd import run_no_stdout
from ..nix import nix_config, nix_eval

log = logging.getLogger(__name__)


@dataclasses.dataclass
class MachineInfo:
    machine_name: str
    machine_description: str | None
    machine_icon: str | None


@API.register
def list_machines(flake_url: str | Path, debug: bool) -> dict[str, MachineInfo]:
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{flake_url}#clanInternals.machines.{system}",
            "--apply",
            """builtins.mapAttrs (name: attrs: {
  inherit (attrs.config.clanCore) machineDescription machineIcon machineName;
})""",
            "--json",
        ]
    )

    proc = run_no_stdout(cmd)

    res = proc.stdout.strip()
    machines_dict = json.loads(res)

    return {
        k: MachineInfo(
            machine_name=v.get("machineName"),
            machine_description=v.get("machineDescription", None),
            machine_icon=v.get("machineIcon", None),
        )
        for k, v in machines_dict.items()
    }


def list_command(args: argparse.Namespace) -> None:
    flake_path = Path(args.flake).resolve()
    print("Listing all machines:\n")
    print("Source: ", flake_path)
    print("-" * 40)
    for name, machine in list_machines(flake_path, args.debug).items():
        description = machine.machine_description or "[no description]"
        print(f"{name}\n: {description}\n")
    print("-" * 40)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
