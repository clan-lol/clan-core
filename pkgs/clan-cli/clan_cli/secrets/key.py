import argparse
from pathlib import Path

from .. import tty
from ..errors import ClanError
from .folders import sops_secrets_folder
from .secrets import collect_keys_for_path, list_secrets
from .sops import (
    default_sops_key_path,
    generate_private_key,
    get_public_key,
    update_keys,
)


def generate_key() -> str:
    path = default_sops_key_path()
    if path.exists():
        raise ClanError(f"Key already exists at {path}")
    priv_key, pub_key = generate_private_key()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(priv_key)
    return pub_key


def show_key() -> str:
    return get_public_key(default_sops_key_path().read_text())


def generate_command(args: argparse.Namespace) -> None:
    pub_key = generate_key()
    tty.info(
        f"Generated age private key at '{default_sops_key_path()}' for your user. Please back it up on a secure location or you will lose access to your secrets."
    )
    tty.info(
        f"Also add your age public key to the repository with 'clan secrets users add youruser {pub_key}' (replace youruser with your user name)"
    )
    pass


def show_command(args: argparse.Namespace) -> None:
    print(show_key())


def update_command(args: argparse.Namespace) -> None:
    flake_dir = Path(args.flake)
    for name in list_secrets(flake_dir):
        secret_path = sops_secrets_folder(flake_dir) / name
        update_keys(
            secret_path,
            list(sorted(collect_keys_for_path(secret_path))),
        )


def register_key_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    parser_generate = subparser.add_parser("generate", help="generate age key")
    parser_generate.set_defaults(func=generate_command)

    parser_show = subparser.add_parser("show", help="show age public key")
    parser_show.set_defaults(func=show_command)

    parser_update = subparser.add_parser(
        "update",
        help="re-encrypt all secrets with current keys (useful when changing keys)",
    )
    parser_update.set_defaults(func=update_command)
