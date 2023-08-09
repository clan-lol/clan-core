import argparse

from . import secrets
from .folders import list_objects, remove_object, sops_machines_folder
from .sops import write_key
from .types import (
    machine_name_type,
    public_or_private_age_key_type,
    secret_name_type,
    validate_hostname,
)


def add_machine(name: str, key: str, force: bool) -> None:
    write_key(sops_machines_folder() / name, key, force)


def remove_machine(name: str) -> None:
    remove_object(sops_machines_folder(), name)


def list_machines() -> list[str]:
    return list_objects(sops_machines_folder(), lambda x: validate_hostname(x))


def add_secret(machine: str, secret: str) -> None:
    secrets.allow_member(
        secrets.machines_folder(secret), sops_machines_folder(), machine
    )


def remove_secret(machine: str, secret: str) -> None:
    secrets.disallow_member(secrets.machines_folder(secret), machine)


def list_command(args: argparse.Namespace) -> None:
    lst = list_machines()
    if len(lst) > 0:
        print("\n".join(lst))


def add_command(args: argparse.Namespace) -> None:
    add_machine(args.machine, args.key, args.force)


def remove_command(args: argparse.Namespace) -> None:
    remove_machine(args.machine)


def add_secret_command(args: argparse.Namespace) -> None:
    add_secret(args.machine, args.secret)


def remove_secret_command(args: argparse.Namespace) -> None:
    remove_secret(args.machine, args.secret)


def register_machines_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    list_parser = subparser.add_parser("list", help="list machines")
    list_parser.set_defaults(func=list_command)

    add_parser = subparser.add_parser("add", help="add a machine")
    add_parser.add_argument(
        "-f",
        "--force",
        help="overwrite existing machine",
        action="store_true",
        default=False,
    )
    add_parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    add_parser.add_argument(
        "key",
        help="public key or private key of the user",
        type=public_or_private_age_key_type,
    )
    add_parser.set_defaults(func=add_command)

    remove_parser = subparser.add_parser("remove", help="remove a machine")
    remove_parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    remove_parser.set_defaults(func=remove_command)

    add_secret_parser = subparser.add_parser(
        "add-secret", help="allow a machine to access a secret"
    )
    add_secret_parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    add_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    add_secret_parser.set_defaults(func=add_secret_command)

    remove_secret_parser = subparser.add_parser(
        "remove-secret", help="remove a group's access to a secret"
    )
    remove_secret_parser.add_argument(
        "machine", help="the name of the group", type=machine_name_type
    )
    remove_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    remove_secret_parser.set_defaults(func=remove_secret_command)
