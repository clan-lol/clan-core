import argparse
import getpass
import os
import subprocess
import sys
from io import StringIO
from pathlib import Path
from typing import IO

from .. import tty
from ..errors import ClanError
from ..nix import nix_shell
from .folders import list_objects, sops_secrets_folder
from .sops import SopsKey, encrypt_file, ensure_sops_key, read_key
from .types import VALID_SECRET_NAME, secret_name_type


def list_command(args: argparse.Namespace) -> None:
    list_objects(
        sops_secrets_folder(), lambda n: VALID_SECRET_NAME.match(n) is not None
    )


def get_command(args: argparse.Namespace) -> None:
    secret: str = args.secret
    ensure_sops_key()
    secret_path = sops_secrets_folder() / secret / "secret"
    if not secret_path.exists():
        raise ClanError(f"Secret '{secret}' does not exist")
    cmd = nix_shell(["sops"], ["sops", "--decrypt", str(secret_path)])
    res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
    print(res.stdout, end="")


def encrypt_secret(key: SopsKey, secret: Path, value: IO[str]) -> None:
    keys = set([key.pubkey])
    for kind in ["users", "machines", "groups"]:
        if not (sops_secrets_folder() / kind).is_dir():
            continue
        k = read_key(sops_secrets_folder() / kind)
        keys.add(k)
    encrypt_file(secret / "secret", value, list(sorted(keys)))


def set_command(args: argparse.Namespace) -> None:
    secret: str = args.secret
    key = ensure_sops_key()
    secret_value = os.environ.get("SOPS_NIX_SECRET")
    if secret_value:
        encrypt_secret(key, sops_secrets_folder() / secret, StringIO(secret_value))
    elif tty.is_interactive():
        secret = getpass.getpass(prompt="Paste your secret: ")
        encrypt_secret(key, sops_secrets_folder() / secret, StringIO(secret))
    else:
        encrypt_secret(key, sops_secrets_folder() / secret, sys.stdin)


def remove_command(args: argparse.Namespace) -> None:
    secret: str = args.secret
    path = sops_secrets_folder() / secret
    if not path.exists():
        raise ClanError(f"Secret '{secret}' does not exist")
    path.unlink()


def add_secret_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("secret", help="the name of the secret", type=secret_name_type)


def allow_member(group_folder: Path, source_folder: Path, name: str) -> None:
    source = source_folder / name
    if not source.exists():
        raise ClanError(f"{name} does not exist in {source_folder}")
    group_folder.mkdir(parents=True, exist_ok=True)
    user_target = group_folder / name
    if user_target.exists():
        if not user_target.is_symlink():
            raise ClanError(
                f"Cannot add user {name}. {user_target} exists but is not a symlink"
            )
        os.remove(user_target)
    user_target.symlink_to(source)


def disallow_member(group_folder: Path, name: str) -> None:
    target = group_folder / name
    if not target.exists():
        raise ClanError(f"{name} does not exist in group in {group_folder}")
    os.remove(target)

    if len(os.listdir(group_folder)) == 0:
        os.rmdir(group_folder)

    if len(os.listdir(group_folder.parent)) == 0:
        os.rmdir(group_folder.parent)


def machines_folder(group: str) -> Path:
    return sops_secrets_folder() / group / "machines"


def users_folder(group: str) -> Path:
    return sops_secrets_folder() / group / "users"


def groups_folder(group: str) -> Path:
    return sops_secrets_folder() / group / "groups"


def register_secrets_parser(subparser: argparse._SubParsersAction) -> None:
    parser_list = subparser.add_parser("list", help="list secrets")
    parser_list.set_defaults(func=list_command)

    parser_get = subparser.add_parser("get", help="get a secret")
    add_secret_argument(parser_get)
    parser_get.set_defaults(func=get_command)

    parser_set = subparser.add_parser("set", help="set a secret")
    add_secret_argument(parser_set)
    parser_set.set_defaults(func=set_command)

    parser_delete = subparser.add_parser("remove", help="remove a secret")
    add_secret_argument(parser_delete)
    parser_delete.set_defaults(func=remove_command)
