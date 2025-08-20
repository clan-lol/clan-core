import argparse

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_services_for_machine,
)
from clan_lib.flake import require_flake
from clan_lib.machines.list import list_full_machines
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config
from clan_lib.vars.generate import run_generators


def generate_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machines: list[Machine] = list(list_full_machines(flake).values())

    if len(args.machines) > 0:
        machines = list(
            filter(
                lambda m: m.name in args.machines,
                machines,
            )
        )

    # prefetch all vars
    config = nix_config()
    system = config["system"]
    machine_names = [machine.name for machine in machines]
    # test
    flake.precache(
        [
            f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
        ]
    )

    run_generators(
        machines,
        generators=args.generator,
        full_closure=args.regenerate if args.regenerate is not None else False,
        no_sandbox=args.no_sandbox,
    )


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        help="machine to generate facts for. if empty, generate facts for all machines",
        nargs="*",
        default=[],
    )
    add_dynamic_completer(machines_parser, complete_machines)

    service_parser = parser.add_argument(
        "--generator",
        "-g",
        type=str,
        help="execute only the specified generator. If unset, execute all generators",
        default=None,
    )
    add_dynamic_completer(service_parser, complete_services_for_machine)

    parser.add_argument(
        "--regenerate",
        "-r",
        action=argparse.BooleanOptionalAction,
        help="whether to regenerate facts for the specified machine",
        default=None,
    )

    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="disable sandboxing when executing the generator. WARNING: potentially executing untrusted code from external clan modules",
        default=False,
    )

    parser.add_argument(
        "--fake-prompts",
        action="store_true",
        help="automatically fill prompt responses for testing (unsafe)",
        default=False,
    )

    parser.set_defaults(func=generate_command)
