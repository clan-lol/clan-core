import argparse
import logging
import sys

from clan_lib.async_run import AsyncContext, AsyncOpts, AsyncRuntime
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.machines.suggestions import validate_machine_names
from clan_lib.machines.update import deploy_machine
from clan_lib.nix import nix_config
from clan_lib.ssh.remote import Remote

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_tags,
)
from clan_cli.machines.list import list_full_machines, query_machines_by_tags

log = logging.getLogger(__name__)


def update_command(args: argparse.Namespace) -> None:
    try:
        if args.flake is None:
            msg = "Could not find clan flake toplevel directory"
            raise ClanError(msg)

        all_machines: list[Machine] = []
        if args.tags:
            tag_filtered_machines = query_machines_by_tags(args.flake, args.tags)
            if args.machines:
                selected_machines = [
                    name for name in args.machines if name in tag_filtered_machines
                ]
            else:
                selected_machines = list(tag_filtered_machines.keys())
        else:
            selected_machines = (
                args.machines
                if args.machines
                else list(list_full_machines(args.flake).keys())
            )

        if args.tags and not selected_machines:
            msg = f"No machines found with tags: {', '.join(args.tags)}"
            raise ClanError(msg)

        if args.machines:
            validate_machine_names(args.machines, args.flake)

        for machine_name in selected_machines:
            machine = Machine(name=machine_name, flake=args.flake)
            all_machines.append(machine)

        if args.target_host is not None and len(all_machines) > 1:
            msg = "Target Host can only be set for one machines"
            raise ClanError(msg)

        def filter_machine(m: Machine) -> bool:
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

        machines_to_update = all_machines
        implicit_all: bool = len(args.machines) == 0 and not args.tags
        if implicit_all:
            machines_to_update = list(filter(filter_machine, all_machines))

        # machines that are in the list but not included in the update list
        ignored_machines = {m.name for m in all_machines if m not in machines_to_update}

        if not machines_to_update and ignored_machines:
            print(
                "WARNING: No machines to update.\n"
                "The following defined machines were ignored because they\n"
                "- Require explicit update (see 'requireExplicitUpdate')\n",
                "- Might not have the `clan.core.networking.targetHost` nixos option set:\n",
                file=sys.stderr,
            )
            for m in ignored_machines:
                print(m, file=sys.stderr)

        if machines_to_update:
            # Prepopulate the cache
            config = nix_config()
            system = config["system"]
            machine_names = [machine.name for machine in machines_to_update]
            args.flake.precache(
                [
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.deployment.requireExplicitUpdate",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.system.clan.deployment.nixosMobileWorkaround",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.secretModule",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.publicModule",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.settings.secretModule",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.settings.publicModule",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.services",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars._serialized.generators",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.facts.secretUploadDirectory",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.vars.password-store.secretLocation",
                    f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.settings.passBackend",
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
                        deploy_machine,
                        machine=machine,
                        target_host=target_host,
                        build_host=machine.build_host(),
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
        choices=["strict", "ask", "tofu", "none"],
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
    parser.set_defaults(func=update_command)
