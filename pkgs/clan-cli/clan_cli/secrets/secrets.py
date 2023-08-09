import argparse
import getpass
import os
import shutil
import sys
from pathlib import Path
from typing import IO, Union

from .. import tty
from ..errors import ClanError
from .folders import (
    list_objects,
    sops_groups_folder,
    sops_machines_folder,
    sops_secrets_folder,
    sops_users_folder,
)
from .sops import decrypt_file, encrypt_file, ensure_sops_key, read_key, update_keys
from .types import VALID_SECRET_NAME, secret_name_type


def collect_keys_for_type(folder: Path) -> set[str]:
    if not folder.exists():
        return set()
    keys = set()
    for p in folder.iterdir():
        if not p.is_symlink():
            continue
        try:
            target = p.resolve()
        except FileNotFoundError:
            tty.warn(f"Ignoring broken symlink {p}")
            continue
        kind = target.parent.name
        if folder.name != kind:
            tty.warn(f"Expected {p} to point to {folder} but points to {target.parent}")
            continue
        keys.add(read_key(target))
    return keys


def collect_keys_for_path(path: Path) -> set[str]:
    keys = set([])
    keys.update(collect_keys_for_type(path / "machines"))
    keys.update(collect_keys_for_type(path / "users"))
    groups = path / "groups"
    if not groups.is_dir():
        return keys
    for group in groups.iterdir():
        keys.update(collect_keys_for_type(group / "machines"))
        keys.update(collect_keys_for_type(group / "users"))
    return keys


def encrypt_secret(
    secret: Path,
    value: Union[IO[str], str],
    add_users: list[str] = [],
    add_machines: list[str] = [],
    add_groups: list[str] = [],
) -> None:
    key = ensure_sops_key()
    keys = set([])

    for user in add_users:
        allow_member(users_folder(secret.name), sops_users_folder(), user, False)

    for machine in add_machines:
        allow_member(
            machines_folder(secret.name), sops_machines_folder(), machine, False
        )

    for group in add_groups:
        allow_member(groups_folder(secret.name), sops_groups_folder(), group, False)

    keys = collect_keys_for_path(secret)

    if key.pubkey not in keys:
        keys.add(key.pubkey)
        allow_member(
            users_folder(secret.name), sops_users_folder(), key.username, False
        )

    encrypt_file(secret / "secret", value, list(sorted(keys)))


def remove_secret(secret: str) -> None:
    path = sops_secrets_folder() / secret
    if not path.exists():
        raise ClanError(f"Secret '{secret}' does not exist")
    shutil.rmtree(path)


def remove_command(args: argparse.Namespace) -> None:
    remove_secret(args.secret)


def add_secret_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("secret", help="the name of the secret", type=secret_name_type)


def machines_folder(group: str) -> Path:
    return sops_secrets_folder() / group / "machines"


def users_folder(group: str) -> Path:
    return sops_secrets_folder() / group / "users"


def groups_folder(group: str) -> Path:
    return sops_secrets_folder() / group / "groups"


def list_directory(directory: Path) -> str:
    if not directory.exists():
        return "{directory} does not exist"
    msg = f"\n{directory} contains:"
    for f in directory.iterdir():
        msg += f"\n  {f.name}"
    return msg


def allow_member(
    group_folder: Path, source_folder: Path, name: str, do_update_keys: bool = True
) -> None:
    source = source_folder / name
    if not source.exists():
        msg = f"{name} does not exist in {source_folder}"
        msg += list_directory(source_folder)
        raise ClanError(msg)
    group_folder.mkdir(parents=True, exist_ok=True)
    user_target = group_folder / name
    if user_target.exists():
        if not user_target.is_symlink():
            raise ClanError(
                f"Cannot add user {name}. {user_target} exists but is not a symlink"
            )
        os.remove(user_target)

    user_target.symlink_to(os.path.relpath(source, user_target.parent))
    if do_update_keys:
        update_keys(
            group_folder.parent,
            list(sorted(collect_keys_for_path(group_folder.parent))),
        )


def disallow_member(group_folder: Path, name: str) -> None:
    target = group_folder / name
    if not target.exists():
        msg = f"{name} does not exist in group in {group_folder}"
        msg += list_directory(group_folder)
        raise ClanError(msg)

    keys = collect_keys_for_path(group_folder.parent)

    if len(keys) < 2:
        raise ClanError(
            f"Cannot remove {name} from {group_folder.parent.name}. No keys left. Use 'clan secrets remove {name}' to remove the secret."
        )
    os.remove(target)

    if len(os.listdir(group_folder)) == 0:
        os.rmdir(group_folder)

    if len(os.listdir(group_folder.parent)) == 0:
        os.rmdir(group_folder.parent)

    update_keys(
        target.parent.parent, list(sorted(collect_keys_for_path(group_folder.parent)))
    )


def list_secrets() -> list[str]:
    return list_objects(
        sops_secrets_folder(), lambda n: VALID_SECRET_NAME.match(n) is not None
    )


def list_command(args: argparse.Namespace) -> None:
    lst = list_secrets()
    if len(lst) > 0:
        print("\n".join(lst))


def get_command(args: argparse.Namespace) -> None:
    secret: str = args.secret
    ensure_sops_key()
    secret_path = sops_secrets_folder() / secret / "secret"
    if not secret_path.exists():
        raise ClanError(f"Secret '{secret}' does not exist")
    print(decrypt_file(secret_path), end="")


def set_command(args: argparse.Namespace) -> None:
    env_value = os.environ.get("SOPS_NIX_SECRET")
    secret_value: Union[str, IO[str]] = sys.stdin
    if env_value:
        secret_value = env_value
    elif tty.is_interactive():
        secret_value = getpass.getpass(prompt="Paste your secret: ")
    encrypt_secret(
        sops_secrets_folder() / args.secret,
        secret_value,
        args.user,
        args.machine,
        args.group,
    )


def register_secrets_parser(subparser: argparse._SubParsersAction) -> None:
    parser_list = subparser.add_parser("list", help="list secrets")
    parser_list.set_defaults(func=list_command)

    parser_get = subparser.add_parser("get", help="get a secret")
    add_secret_argument(parser_get)
    parser_get.set_defaults(func=get_command)

    parser_set = subparser.add_parser("set", help="set a secret")
    add_secret_argument(parser_set)
    parser_set.add_argument(
        "--group",
        type=str,
        action="append",
        default=[],
        help="the group to import the secrets to",
    )
    parser_set.add_argument(
        "--machine",
        type=str,
        action="append",
        default=[],
        help="the machine to import the secrets to",
    )
    parser_set.add_argument(
        "--user",
        type=str,
        action="append",
        default=[],
        help="the user to import the secrets to",
    )
    parser_set.set_defaults(func=set_command)

    parser_delete = subparser.add_parser("remove", help="remove a secret")
    add_secret_argument(parser_delete)
    parser_delete.set_defaults(func=remove_command)
