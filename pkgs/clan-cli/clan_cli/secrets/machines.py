import argparse

from ..machines.types import machine_name_type, validate_hostname
from . import secrets
from .folders import list_objects, remove_object, sops_machines_folder
from .sops import read_key, write_key
from .types import public_or_private_age_key_type, secret_name_type


def add_machine(flake_name: str, name: str, key: str, force: bool) -> None:
    write_key(sops_machines_folder(flake_name) / name, key, force)


def remove_machine(flake_name: str, name: str) -> None:
    remove_object(sops_machines_folder(flake_name), name)


def get_machine(flake_name: str, name: str) -> str:
    return read_key(sops_machines_folder(flake_name) / name)


def has_machine(flake_name: str, name: str) -> bool:
    return (sops_machines_folder(flake_name) / name / "key.json").exists()


def list_machines(flake_name: str) -> list[str]:
    path = sops_machines_folder(flake_name)

    def validate(name: str) -> bool:
        return validate_hostname(name) and has_machine(flake_name, name)

    return list_objects(path, validate)


def add_secret(flake_name: str, machine: str, secret: str) -> None:
    secrets.allow_member(
        secrets.machines_folder(flake_name, secret),
        sops_machines_folder(flake_name),
        machine,
    )


def remove_secret(flake_name: str, machine: str, secret: str) -> None:
    secrets.disallow_member(secrets.machines_folder(flake_name, secret), machine)


def list_command(args: argparse.Namespace) -> None:
    lst = list_machines(args.flake)
    if len(lst) > 0:
        print("\n".join(lst))


def add_command(args: argparse.Namespace) -> None:
    add_machine(args.flake, args.machine, args.key, args.force)


def get_command(args: argparse.Namespace) -> None:
    print(get_machine(args.flake, args.machine))


def remove_command(args: argparse.Namespace) -> None:
    remove_machine(args.flake, args.machine)


def add_secret_command(args: argparse.Namespace) -> None:
    add_secret(args.flake, args.machine, args.secret)


def remove_secret_command(args: argparse.Namespace) -> None:
    remove_secret(args.flake, args.machine, args.secret)


def register_machines_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    # Parser
    list_parser = subparser.add_parser("list", help="list machines")
    list_parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    list_parser.set_defaults(func=list_command)

    # Parser
    add_parser = subparser.add_parser("add", help="add a machine")
    add_parser.add_argument(
        "-f",
        "--force",
        help="overwrite existing machine",
        action="store_true",
        default=False,
    )
    add_parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
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

    # Parser
    get_parser = subparser.add_parser("get", help="get a machine public key")
    get_parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    get_parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    get_parser.set_defaults(func=get_command)

    # Parser
    remove_parser = subparser.add_parser("remove", help="remove a machine")
    remove_parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    remove_parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    remove_parser.set_defaults(func=remove_command)

    # Parser
    add_secret_parser = subparser.add_parser(
        "add-secret", help="allow a machine to access a secret"
    )
    add_secret_parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    add_secret_parser.add_argument(
        "machine", help="the name of the machine", type=machine_name_type
    )
    add_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    add_secret_parser.set_defaults(func=add_secret_command)

    # Parser
    remove_secret_parser = subparser.add_parser(
        "remove-secret", help="remove a group's access to a secret"
    )
    remove_secret_parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    remove_secret_parser.add_argument(
        "machine", help="the name of the group", type=machine_name_type
    )
    remove_secret_parser.add_argument(
        "secret", help="the name of the secret", type=secret_name_type
    )
    remove_secret_parser.set_defaults(func=remove_secret_command)
