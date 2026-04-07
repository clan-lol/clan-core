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
            no_secrets=args.no_secrets,
            use_sandbox=not args.no_sandbox,
        )

        build_outputs: list[BuildResult] = []
        errors: dict[str, Exception] = {}

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
                machine_name = machines_to_build[i].name
                aresult = future.get_result()
                if aresult is None:
                    msg = "Build result should never be None"
                    raise ClanError(msg)
                if aresult.error is not None:
                    errors[machine_name] = aresult.error
                    continue
                build_outputs.append(aresult.result)

        for output in build_outputs:
            print(output.build_path)

        for machine_name, error in errors.items():
            msg = f"Build failed for {machine_name}: {error}"
            raise ClanError(msg) from error

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
        help="Build format: 'toplevel' for special builds, or any format name for config.system.build.images.{format} (e.g., 'iso', 'sd-card'). Default: %(default)s.",
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

    parser.add_argument(
        "--no-secrets",
        action="store_true",
        help="Do not embed secrets into the built image. By default, image formats (e.g., iso) embed the machine's secret decryption key.",
    )

    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="Disable sandboxing when executing generators and image scripts. WARNING: potentially executing untrusted code from external clan modules.",
        default=False,
    )

    parser.set_defaults(func=build_command)
