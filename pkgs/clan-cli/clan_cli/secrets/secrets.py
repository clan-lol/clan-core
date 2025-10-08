import argparse
import functools
import getpass
import logging
import os
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import IO

from clan_lib.errors import ClanError
from clan_lib.git import commit_files

from . import sops
from .folders import (
    list_objects,
    sops_groups_folder,
    sops_machines_folder,
    sops_secrets_folder,
    sops_users_folder,
)
from .sops import (
    decrypt_file,
    encrypt_file,
    load_age_plugins,
    read_keys,
    update_keys,
)
from .types import VALID_SECRET_NAME, secret_name_type

log = logging.getLogger(__name__)

# Minimum number of keys required to keep a secret group
MIN_KEYS_FOR_GROUP_REMOVAL = 2


def list_generators_secrets(generators_path: Path) -> list[Path]:
    paths: list[Path] = []
    for generator_path in generators_path.iterdir():
        if not generator_path.is_dir():
            continue

        def validate(generator_path: Path, name: str) -> bool:
            return has_secret(generator_path / name)

        paths.extend(
            generator_path / obj
            for obj in list_objects(
                generator_path,
                functools.partial(validate, generator_path),
            )
        )
    return paths


def list_vars_secrets(flake_dir: Path) -> list[Path]:
    secret_paths = []
    shared_dir = flake_dir / "vars" / "shared"
    if shared_dir.is_dir():
        secret_paths.extend(list_generators_secrets(shared_dir))

    machines_dir = flake_dir / "vars" / "per-machine"
    if machines_dir.is_dir():
        for machine_dir in machines_dir.iterdir():
            if not machine_dir.is_dir():
                continue
            secret_paths.extend(list_generators_secrets(machine_dir))
    return secret_paths


def update_secrets(
    flake_dir: Path,
    filter_secrets: Callable[[Path], bool] = lambda _: True,
    age_plugins: list[str] | None = None,
) -> list[Path]:
    changed_files = []
    secret_paths = [sops_secrets_folder(flake_dir) / s for s in list_secrets(flake_dir)]
    secret_paths.extend(list_vars_secrets(flake_dir))

    for path in secret_paths:
        if not filter_secrets(path):
            continue
        # clean-up non-existent users, groups, and machines
        # from the secret before we update it:
        changed_files.extend(cleanup_dangling_symlinks(path / "users"))
        changed_files.extend(cleanup_dangling_symlinks(path / "groups"))
        changed_files.extend(cleanup_dangling_symlinks(path / "machines"))
        changed_files.extend(
            update_keys(path, collect_keys_for_path(path), age_plugins=age_plugins),
        )
    return changed_files


def cleanup_dangling_symlinks(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    removed: list[Path] = []
    for link in folder.iterdir():
        if link.is_symlink() and not link.exists():
            link.unlink()
            removed.append(folder / link)
    return removed


def collect_keys_for_type(folder: Path) -> set[sops.SopsKey]:
    if not folder.exists():
        return set()
    keys = set()
    for p in folder.iterdir():
        if not p.is_symlink():
            continue
        try:
            target = p.resolve(strict=True)
        except FileNotFoundError:
            log.warning(f"Ignoring broken symlink {p}")
            continue
        kind = target.parent.name
        if folder.name != kind:
            log.warning(
                f"Expected {p} to point to {folder} but points to {target.parent}",
            )
            continue
        keys.update(read_keys(target))
    return keys


def collect_keys_for_path(path: Path) -> set[sops.SopsKey]:
    keys = set()
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
    flake_dir: Path,
    secret_path: Path,
    value: IO[bytes] | str | bytes | None,
    add_users: list[str] | None = None,
    add_machines: list[str] | None = None,
    add_groups: list[str] | None = None,
    git_commit: bool = True,
    age_plugins: list[str] | None = None,
) -> None:
    if add_groups is None:
        add_groups = []
    if add_machines is None:
        add_machines = []
    if add_users is None:
        add_users = []

    admin_keys = sops.ensure_admin_public_keys(flake_dir)

    if not admin_keys:
        msg = (
            "No admin keys found.\n\n"
            "Please run 'clan vars keygen' to generate and set up keys."
        )
        raise ClanError(msg)

    username = next(iter(admin_keys)).username

    # encrypt_secret can be called before the secret has been created
    # so don't try to call sops.update_keys on a non-existent file:
    do_update_keys = False

    files_to_commit = []
    for user in add_users:
        files_to_commit.extend(
            allow_member(
                users_folder(secret_path),
                sops_users_folder(flake_dir),
                user,
                do_update_keys,
                age_plugins=age_plugins,
            ),
        )

    for machine in add_machines:
        files_to_commit.extend(
            allow_member(
                machines_folder(secret_path),
                sops_machines_folder(flake_dir),
                machine,
                do_update_keys,
                age_plugins=age_plugins,
            ),
        )

    for group in add_groups:
        files_to_commit.extend(
            allow_member(
                groups_folder(secret_path),
                sops_groups_folder(flake_dir),
                group,
                do_update_keys,
                age_plugins=age_plugins,
            ),
        )

    recipient_keys = collect_keys_for_path(secret_path)

    if admin_keys not in recipient_keys:
        recipient_keys.update(admin_keys)

        files_to_commit.extend(
            allow_member(
                users_folder(secret_path),
                sops_users_folder(flake_dir),
                username,
                do_update_keys,
                age_plugins=age_plugins,
            ),
        )

    secret_path = secret_path / "secret"
    encrypt_file(secret_path, value, sorted(recipient_keys), age_plugins)
    files_to_commit.append(secret_path)
    if git_commit:
        commit_files(
            files_to_commit,
            flake_dir,
            f"Update secret {secret_path.parent.name}",
        )


def remove_secret(flake_dir: Path, secret: str) -> None:
    path = sops_secrets_folder(flake_dir) / secret
    if not path.exists():
        msg = f"Secret '{secret}' does not exist"
        raise ClanError(msg)
    shutil.rmtree(path)
    commit_files(
        [path],
        flake_dir,
        f"Remove secret {secret}",
    )


def remove_command(args: argparse.Namespace) -> None:
    remove_secret(args.flake.path, args.secret)


def add_secret_argument(parser: argparse.ArgumentParser, autocomplete: bool) -> None:
    secrets_parser = parser.add_argument(
        "secret",
        metavar="secret-name",
        help="the name of the secret",
        type=secret_name_type,
    )
    if autocomplete:
        from clan_cli.completions import (  # noqa: PLC0415
            add_dynamic_completer,
            complete_secrets,
        )

        add_dynamic_completer(secrets_parser, complete_secrets)


def machines_folder(secret_path: Path) -> Path:
    return secret_path / "machines"


def users_folder(secret_path: Path) -> Path:
    return secret_path / "users"


def groups_folder(secret_path: Path) -> Path:
    return secret_path / "groups"


def list_directory(directory: Path) -> str:
    if not directory.exists():
        return f"{directory} does not exist"
    msg = f"\n{directory} contains:"
    for f in directory.iterdir():
        msg += f"\n  {f.name}"
    return msg


def allow_member(
    group_folder: Path,
    source_folder: Path,
    name: str,
    do_update_keys: bool = True,
    age_plugins: list[str] | None = None,
) -> list[Path]:
    source = source_folder / name
    if not source.exists():
        msg = f"Cannot encrypt {group_folder.parent.name} for '{name}'. '{name}' does not exist in {source_folder}: "
        msg += list_directory(source_folder)
        raise ClanError(msg)
    group_folder.mkdir(parents=True, exist_ok=True)
    member = group_folder / name
    if member.exists():
        if not member.is_symlink():
            msg = f"Cannot add user '{name}' to {group_folder.parent.name} secret. {member} exists but is not a symlink"
            raise ClanError(msg)
        # return early if the symlink already points to the correct target
        if member.resolve() == source:
            return []
        member.unlink()

    member.symlink_to(os.path.relpath(source, member.parent))
    changed = [member]
    if do_update_keys:
        changed.extend(
            update_keys(
                group_folder.parent,
                collect_keys_for_path(group_folder.parent),
                age_plugins=age_plugins,
            ),
        )
    return changed


def disallow_member(
    group_folder: Path,
    name: str,
    age_plugins: list[str] | None,
) -> list[Path]:
    target = group_folder / name
    if not target.exists():
        msg = f"{name} does not exist in group in {group_folder}: "
        msg += list_directory(group_folder)
        raise ClanError(msg)

    keys = collect_keys_for_path(group_folder.parent)

    if len(keys) < MIN_KEYS_FOR_GROUP_REMOVAL:
        msg = f"Cannot remove {name} from {group_folder.parent.name}. No keys left. Use 'clan secrets remove {name}' to remove the secret."
        raise ClanError(msg)
    target.unlink()

    if next(group_folder.iterdir(), None) is None:
        group_folder.rmdir()

    if next(group_folder.parent.iterdir(), None) is None:
        group_folder.parent.rmdir()

    return update_keys(
        target.parent.parent,
        collect_keys_for_path(group_folder.parent),
        age_plugins=age_plugins,
    )


def has_secret(secret_path: Path) -> bool:
    return (secret_path / "secret").exists()


def list_secrets(
    flake_dir: Path,
    filter_fn: Callable[[str], bool] | None = None,
) -> list[str]:
    path = sops_secrets_folder(flake_dir)

    def validate(name: str) -> bool:
        return (
            VALID_SECRET_NAME.match(name) is not None
            and has_secret(sops_secrets_folder(flake_dir) / name)
            and (filter_fn is None or filter_fn(name) is True)
        )

    return list_objects(path, validate)


def list_command(args: argparse.Namespace) -> None:
    def filter_fn(name: str) -> bool:
        return args.pattern in name

    lst = list_secrets(args.flake.path, filter_fn if args.pattern else None)
    if len(lst) > 0:
        print("\n".join(lst))


def decrypt_secret(secret_path: Path, age_plugins: list[str] | None) -> str:
    # lopter(2024-10): I can't think of a good way to ensure that we have the
    # private key for the secret. I mean we could collect all private keys we
    # could find and then make sure we have the one for the secret, but that
    # seems complicated for little ux gain?
    path = secret_path / "secret"
    if not path.exists():
        msg = f"Secret '{secret_path!s}' does not exist"
        raise ClanError(msg)
    return decrypt_file(path, age_plugins=age_plugins)


def get_command(args: argparse.Namespace) -> None:
    print(
        decrypt_secret(
            sops_secrets_folder(args.flake.path) / args.secret,
            age_plugins=load_age_plugins(args.flake),
        ),
        end="",
    )


def is_tty_interactive() -> bool:
    """Returns true if the current process is interactive"""
    return sys.stdin.isatty() and sys.stdout.isatty()


def set_command(args: argparse.Namespace) -> None:
    env_value = os.environ.get("SOPS_NIX_SECRET")
    secret_value: str | IO[bytes] | None = sys.stdin.buffer
    if args.edit:
        secret_value = None
    elif env_value:
        secret_value = env_value
    elif is_tty_interactive():
        secret_value = getpass.getpass(prompt="Paste your secret: ")
    encrypt_secret(
        args.flake.path,
        sops_secrets_folder(args.flake.path) / args.secret,
        secret_value,
        args.user,
        args.machine,
        args.group,
        age_plugins=load_age_plugins(args.flake),
    )


def rename_command(args: argparse.Namespace) -> None:
    flake_dir = args.flake.path
    old_path = sops_secrets_folder(flake_dir) / args.secret
    new_path = sops_secrets_folder(flake_dir) / args.new_name
    if not old_path.exists():
        msg = f"Secret '{args.secret}' does not exist"
        raise ClanError(msg)
    if new_path.exists():
        msg = f"Secret '{args.new_name}' already exists"
        raise ClanError(msg)
    old_path.rename(new_path)
    commit_files(
        [old_path, new_path],
        flake_dir,
        f"Rename secret {args.secret} to {args.new_name}",
    )


def register_secrets_parser(subparser: argparse._SubParsersAction) -> None:
    parser_list = subparser.add_parser("list", help="list secrets")
    parser_list.add_argument(
        "pattern",
        nargs="?",
        help="a pattern to filter the secrets. All secrets containing the pattern will be listed.",
    )
    parser_list.set_defaults(func=list_command)

    parser_get = subparser.add_parser("get", help="get a secret")
    add_secret_argument(parser_get, True)
    parser_get.set_defaults(func=get_command)

    parser_set = subparser.add_parser("set", help="set a secret")
    add_secret_argument(parser_set, False)
    set_group_action = parser_set.add_argument(
        "--group",
        type=str,
        action="append",
        default=[],
        help="the group to import the secrets to (can be repeated)",
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_groups,
    )

    add_dynamic_completer(set_group_action, complete_groups)
    machine_parser = parser_set.add_argument(
        "--machine",
        type=str,
        action="append",
        default=[],
        help="the machine to import the secrets to (can be repeated)",
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
    )

    add_dynamic_completer(machine_parser, complete_machines)
    set_user_action = parser_set.add_argument(
        "--user",
        type=str,
        action="append",
        default=[],
        help="the user to import the secrets to (can be repeated)",
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_users,
    )

    add_dynamic_completer(set_user_action, complete_users)
    parser_set.add_argument(
        "-e",
        "--edit",
        action="store_true",
        default=False,
        help="edit the secret with $EDITOR instead of pasting it",
    )
    parser_set.set_defaults(func=set_command)

    parser_rename = subparser.add_parser("rename", help="rename a secret")
    add_secret_argument(parser_rename, True)
    parser_rename.add_argument("new_name", type=str, help="the new name of the secret")
    parser_rename.set_defaults(func=rename_command)

    parser_remove = subparser.add_parser("remove", help="remove a secret")
    add_secret_argument(parser_remove, True)
    parser_remove.set_defaults(func=remove_command)
