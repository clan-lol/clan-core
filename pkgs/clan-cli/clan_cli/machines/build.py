import argparse
import logging
import sys

from clan_lib.async_run import AsyncContext, AsyncOpts, AsyncRuntime
from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.flake.flake import Flake
from clan_lib.machines.actions import ListOptions, MachineFilter, list_machines
from clan_lib.machines.build import BuildOptions, BuildResult, build_machine
from clan_lib.machines.list import instantiate_inventory_to_machines
from clan_lib.machines.machines import Machine
from clan_lib.machines.suggestions import validate_machine_names

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_tags,
)

log = logging.getLogger(__name__)


def get_machines_for_build(
    flake: Flake,
    explicit_names: list[str],
    filter_tags: list[str],
) -> list[Machine]:
    """Get the machines to build based on CLI arguments."""
    machines_with_tags = list_machines(
        flake,
        ListOptions(filter=MachineFilter(tags=filter_tags)),
    )

    if filter_tags and not machines_with_tags:
        msg = f"No machines found with tags: {' AND '.join(filter_tags)}"
        raise ClanError(msg)

    if not explicit_names:
        return list(
            instantiate_inventory_to_machines(
                flake, {name: m.data for name, m in machines_with_tags.items()}
            ).values()
        )

    machines_to_build = []
    valid_names = validate_machine_names(explicit_names, flake)

    for name in valid_names:
        if filter_tags:
            machine = machines_with_tags.get(name)
            if not machine:
                continue
        else:
            all_machines_dict = list_machines(flake)
            machine = all_machines_dict.get(name)
            if not machine:
                msg = f"Machine '{name}' not found"
                raise ClanError(msg)

        machines_to_build.append(Machine.from_inventory(name, flake, machine.data))

    if not machines_to_build and filter_tags:
        msg = f"No specified machines found with tags: {' AND '.join(filter_tags)}"
        raise ClanError(msg)

    return machines_to_build


def print_build_results(results: list[BuildResult]) -> None:
    """Print build results in a human-readable format."""
    if not results:
        print("No builds completed.")
        return

    successful = []
    failed = []

    for result in results:
        if result.success:
            successful.append(result)
        else:
            failed.append(result)

    total = len(results)

    print(f"\nBuild completed: {len(successful)}/{total} successful")

    if successful:
        print("\n✓ Successful:")
        for result in successful:
            if result.symlink_path:
                print(f"  {result.machine_name} -> {result.symlink_path}")
            else:
                print(f"  {result.machine_name}")

    if failed:
        print("\n✗ Failed:")
        for result in failed:
            print(f"  {result.machine_name}")

    if failed:
        print("\nUse --debug for detailed error information")


def build_command(args: argparse.Namespace) -> None:
    """Build machine configurations."""
    try:
        flake = require_flake(args.flake)

        machines_to_build = get_machines_for_build(
            flake=flake,
            explicit_names=args.machines,
            filter_tags=args.tags,
        )

        if not machines_to_build:
            print("No machines to build.")
            return

        print(f"Building {len(machines_to_build)} machine(s)...")
        if args.format != "toplevel":
            print(f"Format: {args.format}")

        build_options = BuildOptions(
            format=args.format,
            dry_run=args.dry_run,
            no_link=args.no_link,
        )

        all_results = []

        with AsyncRuntime() as runtime:
            futures = []
            for machine in machines_to_build:
                future = runtime.async_run(
                    AsyncOpts(
                        tid=machine.name,
                        async_ctx=AsyncContext(prefix=machine.name),
                    ),
                    build_machine,
                    machine=machine,
                    options=build_options,
                )
                futures.append(future)

            runtime.join_all()

            for i, future in enumerate(futures):
                try:
                    async_result = future.wait()
                    all_results.append(async_result.result)
                except ClanError as e:
                    machine_name = machines_to_build[i].name
                    failed_result = BuildResult(
                        machine_name=machine_name,
                        success=False,
                        error_message=str(e),
                    )
                    all_results.append(failed_result)

        print_build_results(all_results)

        failed_count = sum(1 for r in all_results if not r.success)
        if failed_count > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)


def register_build_parser(parser: argparse.ArgumentParser) -> None:
    """Register the build subcommand parser."""
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        nargs="*",
        default=[],
        metavar="MACHINE",
        help="Machine(s) to build. If no machines are specified, all machines will be built.",
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
        "--format",
        type=str,
        default="toplevel",
        help="Build format: 'toplevel' or 'vm' for special builds, or any format name for config.system.build.images.{format} (e.g., 'iso', 'sd-card'). Default: %(default)s.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run to validate the configuration without actually building.",
    )

    parser.add_argument(
        "--no-link",
        action="store_true",
        help="Do not create result symlinks.",
    )

    parser.set_defaults(func=build_command)
