import argparse

from .info_disk import register_info_disk_parser


def register_info_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="template_type",
        description="the template type to show info for",
        help="the template type to show info for",
        required=True,
    )
    disk_parser = subparser.add_parser(
        "disk", help="Show placeholders and valid options for disk templates"
    )

    register_info_disk_parser(disk_parser)
