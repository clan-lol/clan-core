import argparse
import json
import subprocess

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_eval


def get_vm_inspect_info(machine: str) -> dict:
    clan_dir = get_clan_flake_toplevel().as_posix()

    # config = nix_config()
    # system = config["system"]

    return json.loads(
        subprocess.run(
            nix_eval(
                [
                    # f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.clan.virtualisation' # TODO use this
                    f'{clan_dir}#nixosConfigurations."{machine}".config.system.clan.vm.config'
                ]
            ),
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        ).stdout
    )


def inspect(args: argparse.Namespace) -> None:
    print(f"Creating VM for {args.machine}")
    machine = args.machine
    print(get_vm_inspect_info(machine))


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=inspect)
