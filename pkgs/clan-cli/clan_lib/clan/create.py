import logging
from dataclasses import dataclass
from pathlib import Path

from clan_lib.api import API
from clan_lib.cmd import CmdOut, RunOpts, run
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix import nix_command, nix_metadata, nix_shell
from clan_lib.persist.inventory_store import InventorySnapshot, InventoryStore
from clan_lib.templates import (
    InputPrio,
    TemplateName,
    copy_from_nixstore,
    get_template,
)

log = logging.getLogger(__name__)


@dataclass
class CreateClanResponse:
    flake_update: CmdOut | None = None
    git_init: CmdOut | None = None
    git_add: CmdOut | None = None
    git_config_username: CmdOut | None = None
    git_config_email: CmdOut | None = None


@dataclass
class CreateOptions:
    dest: Path
    template_name: str
    src_flake: Flake | None = None
    input_prio: InputPrio | None = None
    setup_git: bool = True
    initial: InventorySnapshot | None = None
    update_clan: bool = True


def git_command(directory: Path, *args: str) -> list[str]:
    return nix_shell(["git"], ["git", "-C", str(directory), *args])


@API.register
def create_clan(opts: CreateOptions) -> CreateClanResponse:
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

    template = get_template(
        TemplateName(opts.template_name),
        "clan",
        input_prio=opts.input_prio,
        clan_dir=opts.src_flake,
    )
    log.info(f"Found template '{template.name}' in '{template.input_variant}'")

    if dest.exists():
        dest /= template.name

    if dest.exists():
        msg = f"Destination directory {dest} already exists"
        raise ClanError(msg)

    src = Path(template.src["path"])

    copy_from_nixstore(src, dest)

    response = CreateClanResponse()

    if opts.setup_git:
        response.git_init = run(git_command(dest, "init"))
        response.git_add = run(git_command(dest, "add", "."))

        # check if username is set
        has_username = run(
            git_command(dest, "config", "user.name"), RunOpts(check=False)
        )
        response.git_config_username = None
        if has_username.returncode != 0:
            response.git_config_username = run(
                git_command(dest, "config", "user.name", "clan-tool")
            )

        has_username = run(
            git_command(dest, "config", "user.email"), RunOpts(check=False)
        )
        if has_username.returncode != 0:
            response.git_config_email = run(
                git_command(dest, "config", "user.email", "clan@example.com")
            )

    if opts.update_clan:
        flake_update = run(nix_command(["flake", "update"]), RunOpts(cwd=dest))
        response.flake_update = flake_update

    if opts.initial:
        inventory_store = InventoryStore(flake=Flake(str(opts.dest)))
        inventory_store.write(opts.initial, message="Init inventory")

    return response
