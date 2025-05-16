import argparse
import logging
import os
from pathlib import Path

from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import maybe_get_admin_public_key
from clan_cli.secrets.users import add_user
from clan_lib.api import API
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


@API.register
def keygen(flake_dir: Path, user: str | None = None, force: bool = False) -> None:
    if user is None:
        user = os.getenv("USER", None)
        if not user:
            msg = "No user provided and $USER is not set. Please provide a user via --user."
            raise ClanError(msg)
    pub_key = maybe_get_admin_public_key()
    if not pub_key:
        pub_key = generate_key()
    # TODO set flake_dir=flake.path / "vars"
    add_user(
        flake_dir=flake_dir,
        name=user,
        keys=[pub_key],
        force=force,
    )


def _command(
    args: argparse.Namespace,
) -> None:
    keygen(
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
