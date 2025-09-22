import argparse
import logging
import re
from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.dirs import get_clan_flake_toplevel_or_env
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.git import commit_file
from clan_lib.nix_models.clan import InventoryMachine
from clan_lib.nix_models.clan import InventoryMachineDeploy as MachineDeploy
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.patch_engine import merge_objects
from clan_lib.persist.path_utils import set_value_by_path
from clan_lib.templates.handler import machine_template

from clan_cli.completions import add_dynamic_completer, complete_tags

log = logging.getLogger(__name__)


@dataclass
class CreateOptions:
    clan_dir: Flake
    machine: InventoryMachine
    template: str = "new-machine"
    target_host: str | None = None


@API.register
def create_machine(
    opts: CreateOptions,
    commit: bool = True,
) -> None:
    """Create a new machine in the clan directory.

    This function will create a new machine based on a template.

    :param opts: Options for creating the machine, including clan directory, machine details, and template name.
    :param commit: Whether to commit the changes to the git repository.
    :param _persist: Temporary workaround for 'morph'. Whether to persist the changes to the inventory store.
    """
    if not opts.clan_dir.is_local:
        msg = f"Clan {opts.clan_dir} is not a local clan."
        description = "Import machine only works on local clans"
        raise ClanError(msg, description=description)

    clan_dir = opts.clan_dir.path

    machine_name = opts.machine.get("name")
    if not machine_name:
        msg = "Machine name is required"
        raise ClanError(msg, location="Create Machine")

    # TODO: Move this into nix code
    hostname_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
    if not re.match(hostname_regex, machine_name):
        msg = "Machine name must be a valid hostname"
        raise ClanError(msg, location="Create Machine")

    with machine_template(
        flake=opts.clan_dir,
        template_ident=opts.template,
        dst_machine_name=machine_name,
    ) as _machine_dir:
        # Write to the inventory if persist is true
        inventory_store = InventoryStore(opts.clan_dir)
        inventory = inventory_store.read()
        if machine_name in inventory.get("machines", {}):
            msg = f"Machine {machine_name} already exists in inventory"
            description = (
                "Please delete the existing machine or import with a different name"
            )
            raise ClanError(msg, description=description)
        # Committing the machines directory can add the machine with
        # defaults to the eval result of inventory
        if commit:
            commit_file(
                clan_dir / "machines" / machine_name,
                repo_dir=clan_dir,
                commit_message=f"Add machine {machine_name}",
            )
        opts.clan_dir.invalidate_cache()
        inventory = inventory_store.read()

        curr_machine = inventory.get("machines", {}).get(machine_name, {})
        new_machine = merge_objects(curr_machine, opts.machine)

        set_value_by_path(
            inventory,
            f"machines.{machine_name}",
            new_machine,
        )
        inventory_store.write(inventory, message=f"machine '{machine_name}'")

    # Invalidate the cache since this modified the flake
    opts.clan_dir.invalidate_cache()


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

    machine = InventoryMachine(
        name=args.machine_name,
        tags=args.tags,
        deploy=MachineDeploy(targetHost=args.target_host),
    )
    opts = CreateOptions(
        clan_dir=clan_dir,
        machine=machine,
        template=args.template,
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
        "--target-host",
        type=str,
        help="Address of the machine to install and update, in the format of user@host:1234",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        help="""Reference to the template to use for the machine. default="new-machine". In the format '<flake_ref>#template_name' Where <flake_ref> is a flake reference (e.g. github:org/repo) or a local path (e.g. '.' ).
        Omitting '<flake_ref>#' will use the builtin templates (e.g. just 'new-machine' from clan-core ).
        """,
        default="new-machine",
    )
