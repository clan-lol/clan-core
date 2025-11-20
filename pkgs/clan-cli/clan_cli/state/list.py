import argparse
import json
import logging

from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import get_clan_flake_toplevel_or_env
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_eval

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_state_services_for_machine,
)

log = logging.getLogger(__name__)


def list_state_folders(machine: Machine, service: None | str = None) -> None:
    # Use the flake from the machine object (which comes from CLI --flake argument)
    flake = machine.flake.path
    cmd = nix_eval(
        [
            f"{flake}#nixosConfigurations.{machine.name}.config.clan.core.state",
            "--json",
        ],
    )
    res = "{}"

    try:
        proc = run(cmd, RunOpts(prefix=machine.name))
        res = proc.stdout.strip()
    except ClanCmdError as e:
        msg = "Failed to evaluate machine state configuration"
        raise ClanError(
            msg,
            location=f"clan state list {machine.name}",
            description="Evaluation failed on clan.core.state attribute",
        ) from e

    state = json.loads(res)
    if service:
        if state_info := state.get(service):
            state = {service: state_info}
        else:
            msg = f"Service {service} isn't configured for this machine."
            raise ClanError(
                msg,
                location=f"clan state list {machine.name} --service {service}",
                description=f"The service: {service} needs to be configured for the machine.",
            )

    for svc in state:
        if not svc:
            continue

        print(f"· service: {svc}")
        service_cfg = state.get(svc)

        if not service_cfg:
            continue  # or handle missing config

        folders = service_cfg.get("folders")
        if folders:
            print("  folders:")
            for folder in folders:
                print(f"  - {folder}")

        pre_backup = service_cfg.get("preBackupCommand")
        if pre_backup:
            print(f"  preBackupCommand: {pre_backup}")

        post_backup = service_cfg.get("postBackupCommand")
        if post_backup:
            print(f"  postBackupCommand: {post_backup}")

        pre_restore = service_cfg.get("preRestoreCommand")
        if pre_restore:
            print(f"  preRestoreCommand: {pre_restore}")

        post_restore = service_cfg.get("postRestoreCommand")
        if post_restore:
            print(f"  postRestoreCommand: {post_restore}")

        print()


def list_command(args: argparse.Namespace) -> None:
    if args.flake:
        flake = args.flake
    else:
        tmp = get_clan_flake_toplevel_or_env()
        flake = Flake(str(tmp)) if tmp else None

    if not flake:
        msg = "No clan found."
        description = (
            "Run this command in a clan directory or specify the --flake option"
        )
        raise ClanError(msg, description=description)

    list_state_folders(Machine(name=args.machine, flake=flake), service=args.service)


def register_state_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to list state files for",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    service_parser = parser.add_argument(
        "--service",
        help="the service to show state files for",
    )
    add_dynamic_completer(service_parser, complete_state_services_for_machine)
    parser.set_defaults(func=list_command)
