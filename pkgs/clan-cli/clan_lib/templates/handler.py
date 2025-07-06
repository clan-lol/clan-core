import logging
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from clan_lib.dirs import specific_machine_dir
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.machines.machines import Machine
from clan_lib.templates.filesystem import copy_from_nixstore, realize_nix_path
from clan_lib.templates.template_url import transform_url

log = logging.getLogger(__name__)


@contextmanager
def machine_template(
    flake: Flake, template_ident: str, dst_machine_name: str
) -> Iterator[Path]:
    """
    Create a machine from a template.
    This function will copy the template files to the machine specific directory of the specified flake.

    :param flake: The flake to create the machine in.
    :param template_ident: The identifier of the template to use. Example ".#template_name"
    :param dst_machine_name: The name of the machine to create.

    Example usage:

    >>> with machine_template(
    ...     Flake("/home/johannes/git/clan-core"), ".#new-machine", "my-machine"
    ... ) as machine_path:
    ...     # Use `machine_path` here if you want to access the created machine directory

    ... The machine directory is removed if the context raised any errors.
    ... Only if the context is exited without errors, the machine directory is kept.
    """

    # Check for duplicates
    if dst_machine_name in list_machines(flake):
        msg = f"Machine '{dst_machine_name}' already exists"
        raise ClanError(
            msg,
            description="Please remove the existing machine or choose a different name",
        )

    # Get the clan template from the specifier
    [flake_ref, template_selector] = transform_url(
        "machine", template_ident, flake=flake
    )
    # For pretty error messages
    printable_template_ref = f"{flake_ref}#{template_selector}"

    template_flake = Flake(flake_ref)
    try:
        template = template_flake.select(template_selector)
    except ClanError as e:
        msg = f"Failed to select template '{template_ident}' from flake '{flake_ref}' (via attribute path: {printable_template_ref})"
        raise ClanError(msg) from e

    src = template.get("path")
    if not src:
        msg = f"Malformed template: {printable_template_ref} does not have a 'path' attribute"
        raise ClanError(msg)

    src_path = Path(src).resolve()

    realize_nix_path(template_flake, str(src_path))

    if not src_path.exists():
        msg = f"Template {printable_template_ref} does not exist at {src_path}"
        raise ClanError(msg)

    if not src_path.is_dir():
        msg = f"Template {printable_template_ref} is not a directory at {src_path}"
        raise ClanError(msg)

    tmp_machine = Machine(flake=flake, name=dst_machine_name)

    dst_machine_dir = specific_machine_dir(tmp_machine)

    dst_machine_dir.parent.mkdir(exist_ok=True, parents=True)

    copy_from_nixstore(src_path, dst_machine_dir)

    try:
        yield dst_machine_dir
    except Exception as e:
        log.error(f"An error occurred inside the 'machine_template' context: {e}")

        # Ensure that the directory is removed to avoid half-created machines
        # Everything in the with block is considered part of the context
        # So if the context raises an error, we clean up the machine directory
        log.info(f"Removing left-over machine directory: {dst_machine_dir}")
        shutil.rmtree(dst_machine_dir, ignore_errors=True)
        raise
    finally:
        # If no error occurred, the machine directory is kept
        pass


@contextmanager
def clan_template(flake: Flake, template_ident: str, dst_dir: Path) -> Iterator[Path]:
    """
    Create a clan from a template.
    This function will copy the template files to a new clan directory

    :param flake: The flake to create the machine in.
    :param template_ident: The identifier of the template to use. Example ".#template_name"
    :param dst: The name of the directory to create.


    Example usage:

    >>> with clan_template(
    ...     Flake("/home/johannes/git/clan-core"), ".#new-machine", "my-machine"
    ... ) as clan_dir:
    ...     # Use `clan_dir` here if you want to access the created directory

    ... The directory is removed if the context raised any errors.
    ... Only if the context is exited without errors, it is kept.
    """

    # Get the clan template from the specifier
    [flake_ref, template_selector] = transform_url("clan", template_ident, flake=flake)
    # For pretty error messages
    printable_template_ref = f"{flake_ref}#{template_selector}"

    template_flake = Flake(flake_ref)

    try:
        template = template_flake.select(template_selector)
    except ClanError as e:
        msg = f"Failed to select template '{template_ident}' from flake '{flake_ref}' (via attribute path: {printable_template_ref})"
        raise ClanError(msg) from e

    src = template.get("path")
    if not src:
        msg = f"Malformed template: {printable_template_ref} does not have a 'path' attribute"
        raise ClanError(msg)

    src_path = Path(src).resolve()

    realize_nix_path(template_flake, str(src_path))

    if not src_path.exists():
        msg = f"Template {printable_template_ref} does not exist at {src_path}"
        raise ClanError(msg)

    if not src_path.is_dir():
        msg = f"Template {printable_template_ref} is not a directory at {src_path}"
        raise ClanError(msg)

    if dst_dir.exists():
        msg = f"Destination directory {dst_dir} already exists"
        raise ClanError(msg)

    copy_from_nixstore(src_path, dst_dir)

    try:
        yield dst_dir
    except Exception as e:
        log.error(f"An error occurred inside the 'clan_template' context: {e}")
        log.info(f"Removing left-over directory: {dst_dir}")
        shutil.rmtree(dst_dir, ignore_errors=True)
        raise
    finally:
        # If no error occurred, the directory is kept
        pass
