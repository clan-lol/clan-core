import argparse

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import require_flake
from clan_lib.machines.list import list_full_machines
from clan_lib.vars.fix import fix_vars


def fix_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machines = list(list_full_machines(flake).values())

    if len(args.machines) > 0:
        machines = list(
            filter(
                lambda m: m.name in args.machines,
                machines,
            ),
        )

    for machine in machines:
        fix_vars(machine, generator_name=args.generator)


def register_fix_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        help="machine to fix vars for. if empty, fix vars for all machines",
        nargs="*",
        default=[],
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--generator",
        "-g",
        help="the generator to fix",
    )
    parser.set_defaults(func=fix_command)
