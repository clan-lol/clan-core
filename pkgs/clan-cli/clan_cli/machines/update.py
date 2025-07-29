import argparse
import logging
import sys
from typing import get_args

from clan_lib.async_run import AsyncContext, AsyncOpts, AsyncRuntime
from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.flake.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.machines.list import instantiate_inventory_to_machines
from clan_lib.machines.machines import Machine
from clan_lib.machines.suggestions import validate_machine_names
from clan_lib.machines.update import run_machine_update
from clan_lib.nix import nix_config
from clan_lib.ssh.host_key import HostKeyCheck
from clan_lib.ssh.remote import Remote

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_tags,
)

log = logging.getLogger(__name__)


def requires_explicit_update(m: Machine) -> bool:
    try:
        if m.select("config.clan.deployment.requireExplicitUpdate"):
            return False
    except Exception:
        pass

    try:
        # check if the machine has a target host set
        m.target_host  # noqa: B018
    except ClanError:
        return False

    return True


def get_machines_for_update(
    flake: Flake,
    explicit_names: list[str],
    filter_tags: list[str],
) -> list[Machine]:
    all_machines = list_machines(flake)
    machines_with_tags = list_machines(flake, {"filter": {"tags": filter_tags}})

    if filter_tags and not machines_with_tags:
        msg = f"No machines found with tags: {' AND '.join(filter_tags)}"
        raise ClanError(msg)

    # Implicit update all machines / with tags
    # Using tags is not an explicit update
    if not explicit_names:
        machines_to_update = list(
            filter(
                requires_explicit_update,
                instantiate_inventory_to_machines(flake, machines_with_tags).values(),
            )
        )
        # all machines that are in the clan but not included in the update list
        machine_names_to_update = [m.name for m in machines_to_update]
        ignored_machines = {
            m_name for m_name in all_machines if m_name not in machine_names_to_update
        }

        if not machines_to_update and ignored_machines:
            print(
                "WARNING: No machines to update.\n"
                "The following defined machines were ignored because they\n"
                "- Require explicit update (see 'requireExplicitUpdate')\n",
                file=sys.stderr,
            )
            for m in ignored_machines:
                print(m, file=sys.stderr)

        return machines_to_update

    # Else: Explicit update
    machines_to_update = []
    valid_names = validate_machine_names(explicit_names, flake)
    for name in valid_names:
        inventory_machine = machines_with_tags.get(name)
        if not inventory_machine:
            msg = "This is an internal bug"
            raise ClanError(msg)

        machines_to_update.append(
            Machine.from_inventory(name, flake, inventory_machine)
        )

    return machines_to_update


def update_command(args: argparse.Namespace) -> None:
    try:
        flake = require_flake(args.flake)
        machines_to_update = get_machines_for_update(flake, args.machines, args.tags)

        if args.target_host is not None and len(machines_to_update) > 1:
            msg = "Target Host can only be set for one machines"
            raise ClanError(msg)

        # Prepopulate the cache
        config = nix_config()
        system = config["system"]
        machine_names = [machine.name for machine in machines_to_update]
        flake.precache(
            [
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.deployment.requireExplicitUpdate",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.system.clan.deployment.nixosMobileWorkaround",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.secretModule",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.publicModule",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.settings.secretModule",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.settings.publicModule",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.services",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.{{share,dependencies,migrateFact,prompts}}",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.files.*.{{secret,deploy,owner,group,mode,neededFor}}",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.secretUploadDirectory",
            ]
        )

        host_key_check = args.host_key_check
        with AsyncRuntime() as runtime:
            for machine in machines_to_update:
                if args.target_host:
                    target_host = Remote.from_ssh_uri(
                        machine_name=machine.name,
                        address=args.target_host,
                    ).override(host_key_check=host_key_check)
                else:
                    target_host = machine.target_host().override(
                        host_key_check=host_key_check
                    )
                runtime.async_run(
                    AsyncOpts(
                        tid=machine.name,
                        async_ctx=AsyncContext(prefix=machine.name),
                    ),
                    run_machine_update,
                    machine=machine,
                    target_host=target_host,
                    build_host=machine.build_host(),
                    force_fetch_local=args.fetch_local,
                )
            runtime.join_all()
            runtime.check_all()

    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)


def register_update_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        nargs="*",
        default=[],
        metavar="MACHINE",
        help="Machine to update. If no machines are specified, all machines that don't require explicit updates will be updated.",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    tag_parser = parser.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags that machines should be queried for. Multiple tags will intersect.",
    )
    add_dynamic_completer(tag_parser, complete_tags)

    parser.add_argument(
        "--host-key-check",
        choices=list(get_args(HostKeyCheck)),
        default="ask",
        help="Host key (.ssh/known_hosts) check mode.",
    )
    parser.add_argument(
        "--target-host",
        type=str,
        help="Address of the machine to update, in the format of user@host:1234.",
    )
    parser.add_argument(
        "--build-host",
        type=str,
        help="Address of the machine to build the flake, in the format of user@host:1234.",
    )
    parser.add_argument(
        "--fetch-local",
        action="store_true",
        help=(
            "Prefetch flake inputs locally, then upload them to the build-host.\n"
            "This is useful if downloading the inputs requires authentication "
            "which is only available to the local machine"
        ),
    )
    parser.set_defaults(func=update_command)
