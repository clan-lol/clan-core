import argparse

from . import secrets
from .folders import add_key, list_objects, remove_object, sops_users_folder
from .types import (
    VALID_SECRET_NAME,
    public_or_private_age_key_type,
    secret_name_type,
    user_name_type,
)


def add_user(name: str, key: str, force: bool) -> None:
    add_key(sops_users_folder() / name, key, force)


def list_command(args: argparse.Namespace) -> None:
    list_objects(sops_users_folder(), lambda n: VALID_SECRET_NAME.match(n) is not None)


def add_command(args: argparse.Namespace) -> None:
    add_user(args.user, args.key, args.force)


def remove_command(args: argparse.Namespace) -> None:
    remove_object(sops_users_folder(), args.user)


def add_secret_command(args: argparse.Namespace) -> None:
    secrets.allow_member(
        secrets.groups_folder(args.group), sops_users_folder(), args.group
    )


def remove_secret_command(args: argparse.Namespace) -> None:
    secrets.disallow_member(secrets.groups_folder(args.group), args.group)


def register_users_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    list_parser = subparser.add_parser("list", help="list users")
    list_parser.set_defaults(func=list_command)

    add_parser = subparser.add_parser("add", help="add a user")
    add_parser.add_argument(
        "-f", "--force", help="overwrite existing user", action="store_true"
    )
    add_parser.add_argument("user", help="the name of the user", type=user_name_type)
    add_parser.add_argument(
        "key",
        help="public key or private key of the user",
        type=public_or_private_age_key_type,
    )
    add_parser.set_defaults(func=add_command)

    remove_parser = subparser.add_parser("remove", help="remove a user")
    remove_parser.add_argument("user", help="the name of the user", type=user_name_type)
    remove_parser.set_defaults(func=remove_command)

    add_secret_parser = subparser.add_parser(
        "add-secret", help="allow a user to access a secret"
    )
    add_secret_parser.add_argument(
        "user", help="the name of the group", type=user_name_type
    )
    add_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    add_secret_parser.set_defaults(func=add_secret_command)

    add_secret_parser = subparser.add_parser(
        "add-secret", help="allow a machine to access a secret"
    )
    add_secret_parser.add_argument(
        "user", help="the name of the group", type=user_name_type
    )
    add_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    add_secret_parser.set_defaults(func=add_secret_command)

    remove_secret_parser = subparser.add_parser(
        "remove-secret", help="remove a user's access to a secret"
    )
    add_secret_parser.add_argument(
        "user", help="the name of the group", type=user_name_type
    )
    remove_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    remove_secret_parser.set_defaults(func=remove_secret_command)
