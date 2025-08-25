import argparse
import logging
from collections.abc import Sequence
from typing import Any

from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.templates.disk import set_machine_disk_schema

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_templates_disko,
)

log = logging.getLogger(__name__)


class AppendSetAction(argparse.Action):
    def __init__(self, option_strings: str, dest: str, **kwargs: Any) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        lst = getattr(namespace, self.dest)
        if not values or not hasattr(values, "__getitem__"):
            msg = "values must be indexable"
            raise ClanError(msg)
        lst.append((values[0], values[1]))


def apply_command(args: argparse.Namespace) -> None:
    """Apply a disk template to a machine."""
    set_tuples: list[tuple[str, str]] = args.set

    placeholders = dict(set_tuples)

    set_machine_disk_schema(
        Machine(args.machine, args.flake),
        args.template,
        placeholders,
        force=args.force,
        check_hw=not args.skip_hardware_check,
    )
    log.info(f"Applied disk template '{args.template}' to machine '{args.machine}' ")


def register_apply_disk_template_parser(parser: argparse.ArgumentParser) -> None:
    template_action = parser.add_argument(
        "template",
        type=str,
        help="The name of the disk template to apply",
    )
    add_dynamic_completer(template_action, complete_templates_disko)
    machine_action = parser.add_argument(
        "machine",
        type=str,
        help="The machine to apply the template to",
    )
    add_dynamic_completer(machine_action, complete_machines)
    parser.add_argument(
        "--set",
        help="Set a placeholder in the template to a value",
        nargs=2,
        metavar=("placeholder", "value"),
        action=AppendSetAction,
        default=[],
    )
    parser.add_argument(
        "--force",
        help="Force apply the template even if the machine already has a disk schema",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--skip-hardware-check",
        help="Disables hardware checking. By default this command checks that the facter.json report exists and validates provided options",
        action="store_true",
        default=False,
    )

    parser.set_defaults(func=apply_command)
