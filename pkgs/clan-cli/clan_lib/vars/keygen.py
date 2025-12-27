import getpass
import logging
from pathlib import Path

from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import maybe_get_admin_public_keys
from clan_cli.secrets.users import add_user

from clan_lib.api import API
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


def get_user_or_default(user: str | None) -> str:
    """Get the user name, defaulting to the logged-in OS username if not provided."""
    if user is None:
        try:
            user = getpass.getuser()
        except Exception as e:
            msg = "No user provided and could not determine logged-in OS username. Please provide an explicit username via argument"
            raise ClanError(msg) from e
    return user


# TODO: Unify with "create clan" should be done automatically
@API.register
def create_secrets_user(
    flake_dir: Path,
    user: str | None = None,
    force: bool = False,
) -> None:
    """Initialize sops keys for vars"""
    user = get_user_or_default(user)
    pub_keys = maybe_get_admin_public_keys()
    if not pub_keys:
        pub_keys = [generate_key()]
    # TODO set flake_dir=flake.path / "vars"
    add_user(
        flake_dir=flake_dir,
        name=user,
        keys=pub_keys,
        force=force,
    )
