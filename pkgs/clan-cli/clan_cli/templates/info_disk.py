import argparse
import logging

from clan_lib.machines.machines import Machine
from clan_lib.templates.disk import DiskSchema, get_machine_disk_schemas

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_templates_disko,
)

log = logging.getLogger(__name__)


def info_command(args: argparse.Namespace) -> None:
    """Show placeholders and valid options for a disk template."""
    machine = Machine(args.machine, args.flake)
    schemas = get_machine_disk_schemas(machine, check_hw=not args.skip_hardware_check)

    if not args.template:
        available = "\n".join(f"  - {name}" for name in sorted(schemas.keys()))
        print(f"No template specified. Available templates:\n{available}")
        raise SystemExit(1)

    if args.template not in schemas:
        available = "\n".join(f"  - {name}" for name in sorted(schemas.keys()))
        print(
            f"Unknown disk template '{args.template}'. Available templates:\n{available}"
        )
        raise SystemExit(1)

    _print_schema(args.template, schemas[args.template])


def _print_schema(name: str, schema: DiskSchema) -> None:
    print(f"Template: {name}")
    if schema.frontmatter.description:
        print(f"  Description: {schema.frontmatter.description}")

    if not schema.placeholders:
        print("  No placeholders")
        return

    print("  Placeholders:")
    for ph_name, ph in schema.placeholders.items():
        required = " (required)" if ph.required else " (optional)"
        print(f"    --set {ph_name}{required}")
        if ph.label:
            print(f"      Label: {ph.label}")
        if ph.options:
            print("      Valid options:")
            for opt in ph.options:
                print(f"        - {opt}")


def register_info_disk_parser(parser: argparse.ArgumentParser) -> None:
    machine_action = parser.add_argument(
        "machine",
        type=str,
        help="The machine to show disk options for",
    )
    add_dynamic_completer(machine_action, complete_machines)
    template_action = parser.add_argument(
        "template",
        type=str,
        nargs="?",
        default=None,
        help="The disk template to show info for",
    )
    add_dynamic_completer(template_action, complete_templates_disko)
    parser.add_argument(
        "--skip-hardware-check",
        help="Skip hardware check (options won't be shown)",
        action="store_true",
        default=False,
    )
    parser.set_defaults(func=info_command)
