import argparse
import getpass
import logging
import sys
from pathlib import Path

from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import SopsKey, maybe_get_admin_public_keys
from clan_cli.secrets.users import add_user
from clan_lib.api import API
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


def _get_user_or_default(user: str | None) -> str:
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
    flake_dir: Path, user: str | None = None, force: bool = False
) -> None:
    """
    initialize sops keys for vars
    """
    user = _get_user_or_default(user)
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


def _select_keys_interactive(pub_keys: list[SopsKey]) -> list[SopsKey]:
    # let the user select which of the keys to use
    log.info("\nFound existing admin keys on this machine:")
    selected_keys: list[SopsKey] = []
    for i, key in enumerate(pub_keys):
        log.info(
            f"{i + 1}: type: {key.key_type}\n   pubkey: {key.pubkey}\n   source: {key.source}"
        )
    while not selected_keys:
        choice = input(
            "Select keys to use (comma-separated list of numbers, or leave empty to select all): "
        ).strip()
        if not choice:
            log.info("No keys selected, using all keys.")
            return pub_keys

        try:
            indices = [int(i) - 1 for i in choice.split(",")]
            selected_keys = [pub_keys[i] for i in indices if 0 <= i < len(pub_keys)]
        except ValueError:
            log.info("Invalid input. Please enter a comma-separated list of numbers.")

    return selected_keys


def create_secrets_user_interactive(
    flake_dir: Path, user: str | None = None, force: bool = False
) -> None:
    """
    Initialize sops keys for vars interactively.
    """
    user = _get_user_or_default(user)
    pub_keys = maybe_get_admin_public_keys()
    if pub_keys:
        # let the user select which of the keys to use
        pub_keys = _select_keys_interactive(pub_keys)
    else:
        log.info(
            "\nNo admin keys found on this machine, generating a new key for sops."
        )
        pub_keys = [generate_key()]
        # make sure the user backups the generated key
        log.info("\n⚠️  IMPORTANT: Secret Key Backup ⚠️")
        log.info(
            "The generated key above is CRITICAL for accessing your clan's secrets."
        )
        log.info("Without this key, you will lose access to all encrypted data!")
        log.info("Please backup the key file immediately to a secure location.")
        log.info("The key is typically stored in ~/.config/sops/age/keys.txt")
        confirm = None
        while not confirm or confirm.lower() != "y":
            log.info(
                "\nI have backed up the key file to a secure location. Confirm [y/N]: "
            )
            confirm = input().strip().lower()
            if confirm != "y":
                log.error(
                    "You must backup the key before proceeding. This is critical for data recovery!"
                )

    # persist the generated or chosen admin pubkey in the repo
    add_user(
        flake_dir=flake_dir,
        name=user,
        keys=pub_keys,
        force=force,
    )


def create_secrets_user_auto(
    flake_dir: Path, user: str | None = None, force: bool = False
) -> None:
    """
    Detect if the user is in interactive mode or not and choose the appropriate routine.
    """
    if sys.stdin.isatty():
        create_secrets_user_interactive(
            flake_dir=flake_dir,
            user=user,
            force=force,
        )
    else:
        create_secrets_user(
            flake_dir=flake_dir,
            user=user,
            force=force,
        )


def _command(
    args: argparse.Namespace,
) -> None:
    if args.no_interactive:
        create_secrets_user(
            flake_dir=args.flake.path,
            user=args.user,
            force=args.force,
        )
    else:
        create_secrets_user_auto(
            flake_dir=args.flake.path,
            user=args.user,
            force=args.force,
        )


def register_keygen_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--user",
        help="The user to generate the keys for. Default: logged-in OS username (e.g. from $LOGNAME or system)",
        default=None,
    )

    parser.add_argument(
        "-f", "--force", help="overwrite existing user", action="store_true"
    )

    parser.add_argument(
        "--no-interactive",
        help="Run in non-interactive mode, using keys from the machine if available",
        action="store_true",
    )

    parser.set_defaults(func=_command)
