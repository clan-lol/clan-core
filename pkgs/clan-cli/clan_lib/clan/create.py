import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from clan_lib.api import API
from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import clan_templates
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix import nix_command, nix_metadata, nix_shell
from clan_lib.nix_models.clan import InventoryMeta
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import merge_objects, set_value_by_path
from clan_lib.templates.handler import clan_template

log = logging.getLogger(__name__)


@dataclass
class CreateOptions:
    dest: Path
    template: str

    src_flake: Flake | None = None
    setup_git: bool = True
    initial: InventoryMeta | None = None
    update_clan: bool = True

    def validate(self) -> None:
        if self.initial and "name" in self.initial:
            try:
                hostname(self.initial["name"])
            except ClanError as e:
                msg = "must be a valid hostname."
                raise ClanError(
                    msg,
                    location="name",
                    description="The 'name' field must be a valid hostname.",
                ) from e


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
    opts.validate()

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
        flake = Flake(str(opts.dest))

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
            flake.invalidate_cache()

        if opts.setup_git:
            run(git_command(dest, "add", "."))
            run(git_command(dest, "commit", "-m", "Initial commit"))

        if opts.initial:
            inventory_store = InventoryStore(flake)
            inventory = inventory_store.read()
            curr_meta = inventory.get("meta", {})
            new_meta = merge_objects(curr_meta, opts.initial)
            set_value_by_path(inventory, "meta", new_meta)
            inventory_store.write(inventory, message="Init inventory")

    return
