import argparse
import logging

from clan_lib.nix_models.typing import MachineDeployInput, MachineInput

from clan_cli.machines.create import CreateOptions, create_machine

log = logging.getLogger(__name__)


def apply_command(args: argparse.Namespace) -> None:
    """Apply a machine template - actually an alias for machines create --template."""
    # Create machine using the create_machine API directly
    machine = MachineInput(
        name=args.machine,
        tags=[],
        deploy=MachineDeployInput(targetHost=None),
    )

    opts = CreateOptions(
        clan_dir=args.flake,
        machine=machine,
        template=args.template,
    )

    create_machine(opts)


def register_apply_machine_template_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "template",
        type=str,
        help="The name of the machine template to apply",
    )
    parser.add_argument(
        "machine",
        type=str,
        help="The name of the machine to create from the template",
    )

    parser.set_defaults(func=apply_command)
