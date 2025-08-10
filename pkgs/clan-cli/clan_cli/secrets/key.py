import argparse
import json
import logging
import os
import sys

from clan_lib.errors import ClanError
from clan_lib.git import commit_files

from . import sops
from .secrets import update_secrets
from .sops import (
    default_admin_private_key_path,
    generate_private_key,
    load_age_plugins,
)

log = logging.getLogger(__name__)


def generate_key() -> sops.SopsKey:
    """
    Generate a new age key and return it as a SopsKey.

    This function does not check if the key already exists.
    It will generate a new key every time it is called.

    Use 'check_key_exists' to check if a key already exists.
    Before calling this function if you dont want to generate a new key.
    """

    path = default_admin_private_key_path()
    _, pub_key = generate_private_key(out_file=path)
    log.info(
        f"Generated age private key at '{path}' for your user.\nPlease back it up on a secure location or you will lose access to your secrets."
    )
    return sops.SopsKey(
        pub_key, username="", key_type=sops.KeyType.AGE, source=str(path)
    )


def generate_command(args: argparse.Namespace) -> None:
    pub_keys = sops.maybe_get_admin_public_keys()
    if not pub_keys or args.new:
        key = generate_key()
        pub_keys = [key]

    for key in pub_keys:
        key_type = key.key_type.name.lower()
        print(f"{key.key_type.name} key {key.pubkey} is already set", file=sys.stderr)
        print(
            f"Add your {key_type} public key to the repository with:", file=sys.stderr
        )
        print(
            f"clan secrets users add <username> --{key_type}-key {key.pubkey}",
            file=sys.stderr,
        )


def show_command(args: argparse.Namespace) -> None:
    keys = sops.maybe_get_admin_public_keys()
    if not keys:
        msg = "No public key found"
        raise ClanError(msg)
    json.dump([key.as_dict() for key in keys], sys.stdout, indent=2, sort_keys=True)


def update_command(args: argparse.Namespace) -> None:
    flake_dir = args.flake.path
    # Only necessary for the `secrets` test in `clan-infra` currently
    # https://git.clan.lol/clan/clan-infra/src/commit/4cab8e49c3ac0e0395c67abaf789d806807bfb08/checks/secrets.nix
    # TODO: add a `check` command instead that never loads age plugins
    # rather than exposing this escape hatch
    should_load_age_plugins = os.environ.get("CLAN_LOAD_AGE_PLUGINS", "true") != "false"
    commit_files(
        update_secrets(
            flake_dir,
            age_plugins=load_age_plugins(args.flake)
            if should_load_age_plugins
            else None,
        ),
        flake_dir,
        "Updated secrets with new keys",
    )


def register_key_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    parser_generate = subparser.add_parser(
        "generate",
        description=(
            "Generate an age key for the Clan, if you already have an age "
            "or PGP key, then use it to create your user, see: "
            "`clan secrets users add --help'"
        ),
    )
    parser_generate.add_argument(
        "--new",
        help=(
            "Generate a new key, without checking if a key already exists. "
            " This will not overwrite an existing key."
        ),
        action="store_true",
    )
    parser_generate.set_defaults(func=generate_command)

    parser_show = subparser.add_parser("show", help="show public key")
    parser_show.set_defaults(func=show_command)

    parser_update = subparser.add_parser(
        "update",
        help="re-encrypt all secrets with current keys (useful when changing keys)",
    )
    parser_update.set_defaults(func=update_command)
