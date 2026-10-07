import argparse
import logging
import sys
from pathlib import Path

from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import KeyType, SopsKey, maybe_get_admin_public_keys
from clan_cli.secrets.users import add_user
from clan_lib.api.directory import get_clan_dir
from clan_lib.flake import Flake
from clan_lib.nix_selectors import vars_settings_secret_store
from clan_lib.vars.keygen import get_user_or_default

log = logging.getLogger(__name__)


def _select_keys_interactive(pub_keys: list[SopsKey]) -> list[SopsKey]:
    # let the user select which of the keys to use
    log.info("\nFound existing admin keys on this machine:")
    selected_keys: list[SopsKey] = []
    for i, key in enumerate(pub_keys):
        log.info(
            f"{i + 1}: type: {key.key_type}\n   pubkey: {key.pubkey}\n   source: {key.source}",
        )
    while not selected_keys:
        choice = input(
            "Select keys to use (comma-separated list of numbers, or leave empty to select all): ",
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


def select_admin_keys(interactive: bool) -> list[SopsKey]:
    """Pick existing admin keys of this machine, or generate a new age key."""
    pub_keys = maybe_get_admin_public_keys()
    if pub_keys:
        return _select_keys_interactive(pub_keys) if interactive else pub_keys

    if not interactive:
        return [generate_key()]

    log.info("\nNo admin keys found on this machine, generating a new age key.")
    key = generate_key()
    # make sure the user backups the generated key
    log.info("\n⚠️  IMPORTANT: Secret Key Backup ⚠️")
    log.info(
        "The generated key above is CRITICAL for accessing your clan's secrets.",
    )
    log.info("Without this key, you will lose access to all encrypted data!")
    log.info("Please backup the key file immediately to a secure location.")
    log.info(f"The key is stored in {key.source}")
    confirm = None
    while not confirm or confirm.lower() != "y":
        log.info(
            "\nI have backed up the key file to a secure location. Confirm [y/N]: ",
        )
        confirm = input().strip().lower()
        if confirm != "y":
            log.error(
                "You must backup the key before proceeding. This is critical for data recovery!",
            )
    return [key]


def age_recipients(keys: list[SopsKey]) -> list[str]:
    """Public keys usable as recipients of the age vars backend."""
    return [key.pubkey for key in keys if key.key_type == KeyType.AGE]


def register_admin_keys(
    flake_dir: Path,
    keys: list[SopsKey],
    user: str | None = None,
) -> None:
    """Grant the admin keys access to the secrets of a freshly created clan.

    The age backend takes its recipients from clan.nix, which `create_clan`
    already filled in. The sops backend needs a sops user in the repository.
    """
    backend = Flake(str(flake_dir)).select(vars_settings_secret_store())
    if backend == "age":
        if not age_recipients(keys):
            log.warning(
                "None of the selected keys is an age key. Add your age public key "
                "to vars.settings.recipients.default in clan.nix.",
            )
        return
    if backend == "sops":
        add_user(
            clan_dir=flake_dir,
            name=get_user_or_default(user),
            keys=keys,
            force=True,
            flake_dir=flake_dir,
        )


def _create_secrets_user(
    clan_dir: Path,
    flake_dir: Path,
    interactive: bool,
    user: str | None = None,
    force: bool = False,
) -> None:
    """Initialize sops keys for vars."""
    user = get_user_or_default(user)
    add_user(
        clan_dir=clan_dir,
        name=user,
        keys=select_admin_keys(interactive),
        force=force,
        flake_dir=flake_dir,
    )


def _command(
    args: argparse.Namespace,
) -> None:
    flake: Flake = args.flake
    clan_dir = get_clan_dir(flake)
    _create_secrets_user(
        clan_dir=clan_dir,
        flake_dir=flake.path,
        interactive=not args.no_interactive and sys.stdin.isatty(),
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
        "-f",
        "--force",
        help="overwrite existing user",
        action="store_true",
    )

    parser.add_argument(
        "--no-interactive",
        help="Run in non-interactive mode, using keys from the machine if available",
        action="store_true",
    )

    parser.set_defaults(func=_command)
