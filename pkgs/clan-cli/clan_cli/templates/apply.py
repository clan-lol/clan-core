import argparse

from .apply_disk import register_apply_disk_template_parser
from .apply_machine import register_apply_machine_template_parser


def register_apply_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="template_type",
        description="the template type to apply",
        help="the template type to apply",
        required=True,
    )
    disk_parser = subparser.add_parser("disk", help="Apply a disk template")
    machine_parser = subparser.add_parser("machine", help="Apply a machine template")

    register_apply_disk_template_parser(disk_parser)
    register_apply_machine_template_parser(machine_parser)
