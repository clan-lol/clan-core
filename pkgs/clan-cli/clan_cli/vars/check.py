import argparse
import logging

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import require_flake
from clan_lib.machines.list import list_full_machines
from clan_lib.vars.check import check_vars

log = logging.getLogger(__name__)


def check_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machines = list(list_full_machines(flake).values())

    if len(args.machines) > 0:
        machines = list(
            filter(
                lambda m: m.name in args.machines,
                machines,
            ),
        )

    all_ok = True
    for machine in machines:
        ok = check_vars(machine.name, flake, generator_name=args.generator)
        if not ok:
            all_ok = False
    if not all_ok:
        raise SystemExit(1)


def register_check_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        help="machines to check vars for. if empty, check vars for all machines",
        nargs="*",
        default=[],
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--generator",
        "-g",
        help="the generator to check",
    )
    parser.set_defaults(func=check_command)
