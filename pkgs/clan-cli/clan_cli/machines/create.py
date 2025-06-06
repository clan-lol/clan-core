import argparse
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from clan_lib.api import API
from clan_lib.dirs import get_clan_flake_toplevel_or_env
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.git import commit_file
from clan_lib.nix_models.clan import InventoryMachine
from clan_lib.nix_models.clan import InventoryMachineDeploy as MachineDeploy
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path
from clan_lib.templates import (
    InputPrio,
    TemplateName,
    copy_from_nixstore,
    get_template,
)

from clan_cli.completions import add_dynamic_completer, complete_tags
from clan_cli.machines.list import list_machines

log = logging.getLogger(__name__)


@dataclass
class CreateOptions:
    clan_dir: Flake
    machine: InventoryMachine
    target_host: str | None = None
    input_prio: InputPrio | None = None
    template_name: str | None = None


@API.register
def create_machine(
    opts: CreateOptions, commit: bool = True, _persist: bool = True
) -> None:
    """
    Create a new machine in the clan directory.

    This function will create a new machine based on a template.

    :param opts: Options for creating the machine, including clan directory, machine details, and template name.
    :param commit: Whether to commit the changes to the git repository.
    :param _persist: Temporary workaround for 'morph'. Whether to persist the changes to the inventory store.
    """

    if not opts.clan_dir.is_local:
        msg = f"Clan {opts.clan_dir} is not a local clan."
        description = "Import machine only works on local clans"
        raise ClanError(msg, description=description)

    if not opts.template_name:
        opts.template_name = "new-machine"

    clan_dir = opts.clan_dir.path

    # TODO(@Qubasa): make this a proper template handler
    # i.e. with_template (use context manager)
    # And move the checks and template handling into the template handler
    template = get_template(
        TemplateName(opts.template_name),
        "machine",
        input_prio=opts.input_prio,
        clan_dir=opts.clan_dir,
    )
    log.info(f"Found template '{template.name}' in '{template.input_variant}'")

    machine_name = opts.machine.get("name")
    if opts.template_name in list_machines(
        Flake(str(clan_dir))
    ) and not opts.machine.get("name"):
        msg = f"{opts.template_name} is already defined in {clan_dir}"
        raise ClanError(msg)

    machine_name = machine_name if machine_name else opts.template_name
    src = Path(template.src["path"])

    if not src.exists():
        msg = f"Template {template} does not exist"
        raise ClanError(msg)
    if not src.is_dir():
        msg = f"Template {template} is not a directory"
        raise ClanError(msg)

    dst = clan_dir / "machines"
    dst.mkdir(exist_ok=True)
    dst /= machine_name

    # TODO: Move this into nix code
    hostname_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
    if not re.match(hostname_regex, machine_name):
        msg = "Machine name must be a valid hostname"
        raise ClanError(msg, location="Create Machine")

    if dst.exists():
        msg = f"Machine {machine_name} already exists in {clan_dir}"
        description = "Please remove the existing machine folder"
        raise ClanError(msg, description=description)

    # TODO(@Qubasa): move this into the template handler
    if not (src / "configuration.nix").exists():
        msg = f"Template machine '{opts.template_name}' does not contain a configuration.nix"
        description = "Template machine must contain a configuration.nix"
        raise ClanError(msg, description=description)

    # TODO(@Qubasa): move this into the template handler
    copy_from_nixstore(src, dst)

    if _persist:
        target_host = opts.target_host
        new_machine = opts.machine
        new_machine["deploy"] = {"targetHost": target_host}  # type: ignore

        inventory_store = InventoryStore(opts.clan_dir)
        inventory = inventory_store.read()

        if machine_name in inventory.get("machines", {}):
            msg = f"Machine {machine_name} already exists in inventory"
            description = (
                "Please delete the existing machine or import with a different name"
            )
            raise ClanError(msg, description=description)

        set_value_by_path(
            inventory,
            f"machines.{machine_name}",
            new_machine,
        )
        inventory_store.write(inventory, message=f"machine '{machine_name}'")

    opts.clan_dir.invalidate_cache()
    # Commit at the end in that order to avoid committing halve-baked machines
    # TODO: automatic rollbacks if something goes wrong

    if commit:
        commit_file(
            clan_dir / "machines" / machine_name,
            repo_dir=clan_dir,
            commit_message=f"Add machine {machine_name}",
        )


def create_command(args: argparse.Namespace) -> None:
    if args.flake:
        clan_dir = args.flake
    else:
        tmp = get_clan_flake_toplevel_or_env()
        clan_dir = Flake(str(tmp)) if tmp else None

    if not clan_dir:
        msg = "No clan found."
        description = (
            "Run this command in a clan directory or specify the --flake option"
        )
        raise ClanError(msg, description=description)

    if len(args.input) == 0:
        args.input = ["clan", "clan-core"]

    if args.no_self:
        input_prio = InputPrio.try_inputs(tuple(args.input))
    else:
        input_prio = InputPrio.try_self_then_inputs(tuple(args.input))

    machine = InventoryMachine(
        name=args.machine_name,
        tags=args.tags,
        deploy=MachineDeploy(targetHost=args.target_host),
    )
    opts = CreateOptions(
        input_prio=input_prio,
        clan_dir=clan_dir,
        machine=machine,
        template_name=args.template_name,
        target_host=args.target_host,
    )
    create_machine(opts)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=create_command)
    parser.add_argument(
        "machine_name",
        type=str,
        help="The name of the machine to create",
    )
    tag_parser = parser.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags to associate with the machine. Can be used to assign multiple machines to services.",
    )
    add_dynamic_completer(tag_parser, complete_tags)
    parser.add_argument(
        "--template-name",
        type=str,
        help="The name of the template machine to import",
    )
    parser.add_argument(
        "--target-host",
        type=str,
        help="Address of the machine to install and update, in the format of user@host:1234",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="""Flake input name to use as template source
        can be specified multiple times, inputs are tried in order of definition
        Example: --input clan --input clan-core
        """,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--no-self",
        help="Do not look into own flake for templates",
        action="store_true",
        default=False,
    )
