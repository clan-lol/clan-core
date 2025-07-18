import argparse
import logging
import os
from pathlib import Path

from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import maybe_get_admin_public_keys
from clan_cli.secrets.users import add_user
from clan_lib.api import API
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


# TODO: Unify with "create clan" should be done automatically
@API.register
def create_secrets_user(
    flake_dir: Path, user: str | None = None, force: bool = False
) -> None:
    """
    initialize sops keys for vars
    """
    if user is None:
        user = os.getenv("USER", None)
        if not user:
            msg = "No user provided and environment variable: '$USER' is not set. Please provide an explizit username via argument"
            raise ClanError(msg)
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


def _command(
    args: argparse.Namespace,
) -> None:
    create_secrets_user(
        flake_dir=args.flake.path,
        user=args.user,
        force=args.force,
    )


def register_keygen_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--user",
        help="The user to generate the keys for. Default: $USER",
        default=None,
    )

    parser.add_argument(
        "-f", "--force", help="overwrite existing user", action="store_true"
    )

    parser.set_defaults(func=_command)
