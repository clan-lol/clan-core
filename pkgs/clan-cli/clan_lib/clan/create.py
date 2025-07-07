import logging
from dataclasses import dataclass
from pathlib import Path

from clan_lib.api import API
from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import clan_templates
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix import nix_command, nix_metadata, nix_shell
from clan_lib.persist.inventory_store import InventorySnapshot, InventoryStore
from clan_lib.templates.handler import clan_template

log = logging.getLogger(__name__)


@dataclass
class CreateOptions:
    dest: Path
    template: str

    src_flake: Flake | None = None
    setup_git: bool = True
    initial: InventorySnapshot | None = None
    update_clan: bool = True


def git_command(directory: Path, *args: str) -> list[str]:
    return nix_shell(["git"], ["git", "-C", str(directory), *args])


@API.register
def create_clan(opts: CreateOptions) -> None:
    """Create a new clan repository with the specified template.
    Args:
        opts: CreateOptions containing the destination path, template name,
            source flake, and other options.
    Raises:
        ClanError: If the source flake is not a valid flake or if the destination
            directory already exists.
    """

    dest = opts.dest.resolve()

    if opts.src_flake is not None:
        try:
            nix_metadata(str(opts.src_flake))
        except ClanError:
            log.error(
                f"Found a repository, but it is not a valid flake: {opts.src_flake}"
            )
            log.warning("Setting src_flake to None")
            opts.src_flake = None

    if opts.src_flake is None:
        opts.src_flake = Flake(str(clan_templates()))

    with clan_template(
        opts.src_flake, template_ident=opts.template, dst_dir=opts.dest
    ) as _clan_dir:
        if opts.setup_git:
            run(git_command(dest, "init"))
            run(git_command(dest, "add", "."))

            # check if username is set
            has_username = run(
                git_command(dest, "config", "user.name"), RunOpts(check=False)
            )
            if has_username.returncode != 0:
                run(git_command(dest, "config", "user.name", "clan-tool"))

            has_username = run(
                git_command(dest, "config", "user.email"), RunOpts(check=False)
            )
            if has_username.returncode != 0:
                run(git_command(dest, "config", "user.email", "clan@example.com"))

        if opts.update_clan:
            run(nix_command(["flake", "update"]), RunOpts(cwd=dest))

    if opts.initial:
        inventory_store = InventoryStore(flake=Flake(str(opts.dest)))
        inventory_store.write(opts.initial, message="Init inventory")

    return
