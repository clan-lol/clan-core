import argparse
import logging
from typing import TYPE_CHECKING, TypeVar, get_args

from clan_lib.async_run import AsyncContext, AsyncFuture, AsyncOpts, AsyncRuntime
from clan_lib.errors import ClanError, text_heading
from clan_lib.flake import require_flake
from clan_lib.machines.generations import MachineGeneration, get_machine_generations
from clan_lib.machines.machines import Machine
from clan_lib.network.network import get_best_remote
from clan_lib.ssh.host_key import HostKeyCheck
from clan_lib.ssh.localhost import LocalHost
from clan_lib.ssh.remote import Remote

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_tags,
)
from clan_cli.machines.update import get_machines_for_update

if TYPE_CHECKING:
    from clan_lib.ssh.host import Host

log = logging.getLogger(__name__)


def print_generations(generations: list[MachineGeneration]) -> None:
    headers = [
        "Generation",
        "Date",
        "NixOS Version",
        "Kernel Version",
    ]
    rows = []
    for gen in generations:
        gen_marker = " ← current" if gen.current else ""
        gen_str = f"{gen.generation}{gen_marker}"
        row = [
            gen_str,
            gen.date,
            gen.nixos_version,
            gen.kernel_version,
        ]
        rows.append(row)

    elided_rows = rows

    col_widths = [
        max(len(str(item)) for item in [header] + [row[i] for row in elided_rows])
        for i, header in enumerate(headers)
    ]

    # Print header
    header_row = " | ".join(
        header.ljust(col_widths[i]) for i, header in enumerate(headers)
    )
    print(header_row)
    print("-+-".join("-" * w for w in col_widths))

    # Print rows
    for row in elided_rows:
        print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))))

    print()


def print_summary_table(
    machine_data: dict[Machine, list[MachineGeneration]],
) -> None:
    print(text_heading("Current Generations Summary"))
    headers = ["Machine", "Current Generation", "Date", "NixOS Version"]
    rows = []

    for machine, generations in machine_data.items():
        current_gen = None
        for gen in generations:
            if gen.current:
                current_gen = gen
                break

        if current_gen is None:
            continue

        row = [
            machine.name,
            str(current_gen.generation),
            current_gen.date,
            current_gen.nixos_version,
        ]
        rows.append(row)

    if not rows:
        print("Couldn't retrieve data from any machine.")
        return

    col_widths = [
        max(len(str(item)) for item in [header] + [row[i] for row in rows])
        for i, header in enumerate(headers)
    ]

    # Print header
    header_row = " | ".join(
        header.ljust(col_widths[i]) for i, header in enumerate(headers)
    )
    print(header_row)
    print("-+-".join("-" * w for w in col_widths))

    # Print rows
    for row in rows:
        print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))))

    print()


def generations_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)

    machines_to_update = get_machines_for_update(flake, args.machines, args.tags)

    if args.target_host is not None and len(machines_to_update) > 1:
        msg = "Target Host can only be set for one machines"
        raise ClanError(msg)

    host_key_check = args.host_key_check
    machine_generations: dict[Machine, AsyncFuture[list[MachineGeneration]]] = {}
    with AsyncRuntime() as runtime:
        for machine in machines_to_update:
            if args.target_host:
                target_host: Host | None = None
                if args.target_host == "localhost":
                    target_host = LocalHost()
                else:
                    target_host = Remote.from_ssh_uri(
                        machine_name=machine.name,
                        address=args.target_host,
                    ).override(host_key_check=host_key_check)
            else:
                try:
                    with get_best_remote(machine) as _remote:
                        target_host = machine.target_host().override(
                            host_key_check=host_key_check
                        )
                except ClanError:
                    log.warning(
                        f"Skipping {machine.name} as it has no target host configured."
                    )
                    continue
            generations = runtime.async_run(
                AsyncOpts(
                    tid=machine.name,
                    async_ctx=AsyncContext(prefix=machine.name),
                ),
                get_machine_generations,
                target_host=target_host,
            )
            machine_generations[machine] = generations
        runtime.join_all()

    R = TypeVar("R")

    errors: dict[Machine, Exception] = {}
    successful_machines: dict[Machine, list[MachineGeneration]] = {}

    for machine, generations_future in machine_generations.items():

        def get_result(async_future: AsyncFuture[R]) -> R | Exception:
            aresult = async_future.get_result()
            if aresult is None:
                msg = "Generations result should never be None"
                raise ClanError(msg)
            if aresult.error is not None:
                return aresult.error
            return aresult.result

        mgenerations = get_result(generations_future)
        if isinstance(mgenerations, Exception):
            errors[machine] = mgenerations
            continue

        successful_machines[machine] = mgenerations

    # Check if specific machines were requested
    specific_machines_requested = bool(args.machines or args.tags)

    if specific_machines_requested:
        # Print detailed generations for each machine
        for mgenerations in successful_machines.values():
            print_generations(generations=mgenerations)
    else:
        # Print summary table
        print_summary_table(successful_machines)

    for machine, error in errors.items():
        msg = f"Failed for machine {machine.name}: {error}"
        raise ClanError(msg) from error


def register_generations_parser(parser: argparse.ArgumentParser) -> None:
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
    parser.set_defaults(func=generations_command)
