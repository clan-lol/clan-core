import argparse
from pathlib import Path

from clan_lib.flake import require_flake
from clan_lib.git import commit_files

from clan_cli.machines.types import machine_name_type, validate_hostname

from . import secrets, sops
from .filters import get_secrets_filter_for_machine
from .folders import (
    list_objects,
    remove_object,
    sops_machines_folder,
    sops_secrets_folder,
)
from .secrets import update_secrets
from .sops import load_age_plugins, read_key, write_key
from .types import public_or_private_age_key_type, secret_name_type


def add_machine(flake_dir: Path, name: str, pubkey: str, force: bool) -> None:
    machine_path = sops_machines_folder(flake_dir) / name
    write_key(
        machine_path,
        sops.SopsKey(pubkey, "", sops.KeyType.AGE, source=str(machine_path)),
        overwrite=force,
    )
    paths = [machine_path]

    filter_machine_secrets = get_secrets_filter_for_machine(flake_dir, name)
    paths.extend(update_secrets(flake_dir, filter_machine_secrets))
    commit_files(
        paths,
        flake_dir,
        f"Add machine {name} to secrets",
    )


def remove_machine(flake_dir: Path, name: str) -> None:
    removed_paths = remove_object(sops_machines_folder(flake_dir), name)
    filter_machine_secrets = get_secrets_filter_for_machine(flake_dir, name)
    removed_paths.extend(update_secrets(flake_dir, filter_machine_secrets))
    commit_files(
        removed_paths,
        flake_dir,
        f"Remove machine {name}",
    )


def get_machine_pubkey(flake_dir: Path, name: str) -> str:
    key = read_key(sops_machines_folder(flake_dir) / name)
    return key.pubkey


def has_machine(flake_dir: Path, name: str) -> bool:
    """Checks if a machine exists in the sops machines folder"""
    return (sops_machines_folder(flake_dir) / name / "key.json").exists()


def list_sops_machines(flake_dir: Path) -> list[str]:
    """Lists all machines in the sops machines folder"""
    path = sops_machines_folder(flake_dir)

    def validate(name: str) -> bool:
        return validate_hostname(name) and has_machine(flake_dir, name)

    return list_objects(path, validate)


def add_secret(
    flake_dir: Path,
    machine: str,
    secret_path: Path,
    age_plugins: list[str] | None,
) -> None:
    paths = secrets.allow_member(
        secrets.machines_folder(secret_path),
        sops_machines_folder(flake_dir),
        machine,
        age_plugins=age_plugins,
    )
    commit_files(
        paths,
        flake_dir,
        f"Add {machine} to secret",
    )


def remove_secret(
    flake_dir: Path,
    machine: str,
    secret: str,
    age_plugins: list[str] | None,
) -> None:
    updated_paths = secrets.disallow_member(
        secrets.machines_folder(sops_secrets_folder(flake_dir) / secret),
        machine,
        age_plugins=age_plugins,
    )
    commit_files(
        updated_paths,
        flake_dir,
        f"Remove {machine} from secret {secret}",
    )


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    lst = list_sops_machines(flake.path)
    if len(lst) > 0:
        print("\n".join(lst))


def add_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    add_machine(flake.path, args.machine, args.key, args.force)


def get_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    print(get_machine_pubkey(flake.path, args.machine))


def remove_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    remove_machine(flake.path, args.machine)


def add_secret_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    add_secret(
        flake.path,
        args.machine,
        sops_secrets_folder(flake.path) / args.secret,
        age_plugins=load_age_plugins(flake),
    )


def remove_secret_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    remove_secret(
        flake.path,
        args.machine,
        args.secret,
        age_plugins=load_age_plugins(flake),
    )


def register_machines_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    # Parser
    list_parser = subparser.add_parser("list", help="list machines")
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
    add_machine_action = add_parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
    )

    add_dynamic_completer(add_machine_action, complete_machines)
    add_parser.add_argument(
        "key",
        help="public or private age key of the machine",
        type=public_or_private_age_key_type,
    )
    add_parser.set_defaults(func=add_command)

    # Parser
    get_parser = subparser.add_parser("get", help="get a machine public key")
    get_machine_parser = get_parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
    )

    add_dynamic_completer(get_machine_parser, complete_machines)
    get_parser.set_defaults(func=get_command)

    # Parser
    remove_parser = subparser.add_parser("remove", help="remove a machine")
    remove_machine_parser = remove_parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
    )

    add_dynamic_completer(remove_machine_parser, complete_machines)
    remove_parser.set_defaults(func=remove_command)

    # Parser
    add_secret_parser = subparser.add_parser(
        "add-secret",
        help="allow a machine to access a secret",
    )
    machine_add_secret_parser = add_secret_parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
        complete_secrets,
    )

    add_dynamic_completer(machine_add_secret_parser, complete_machines)
    add_secret_action = add_secret_parser.add_argument(
        "secret",
        help="the name of the secret",
        type=secret_name_type,
    )
    add_dynamic_completer(add_secret_action, complete_secrets)
    add_secret_parser.set_defaults(func=add_secret_command)

    # Parser
    remove_secret_parser = subparser.add_parser(
        "remove-secret",
        help="remove a group's access to a secret",
    )
    machine_remove_parser = remove_secret_parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
        complete_secrets,
    )

    add_dynamic_completer(machine_remove_parser, complete_machines)
    remove_secret_action = remove_secret_parser.add_argument(
        "secret",
        help="the name of the secret",
        type=secret_name_type,
    )
    add_dynamic_completer(remove_secret_action, complete_secrets)
    remove_secret_parser.set_defaults(func=remove_secret_command)
