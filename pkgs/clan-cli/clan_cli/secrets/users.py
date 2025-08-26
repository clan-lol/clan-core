import argparse
import json
import logging
import sys
from collections.abc import Iterable
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.git import commit_files

from . import groups, secrets, sops
from .filters import get_secrets_filter_for_user
from .folders import (
    list_objects,
    remove_object,
    sops_groups_folder,
    sops_secrets_folder,
    sops_users_folder,
)
from .secrets import update_secrets
from .sops import append_keys, load_age_plugins, read_keys, remove_keys, write_keys
from .types import (
    VALID_USER_NAME,
    public_or_private_age_key_type,
    secret_name_type,
    user_name_type,
)

log = logging.getLogger(__name__)


def add_user(
    flake_dir: Path,
    name: str,
    keys: Iterable[sops.SopsKey],
    force: bool,
) -> None:
    path = sops_users_folder(flake_dir) / name

    write_keys(path, keys, overwrite=force)
    updated_paths = [path]

    filter_user_secrets = get_secrets_filter_for_user(flake_dir, name)
    updated_paths.extend(update_secrets(flake_dir, filter_user_secrets))
    commit_files(
        updated_paths,
        flake_dir,
        f"Add user {name} to secrets",
    )


def remove_user(flake_dir: Path, name: str) -> None:
    updated_paths: list[Path] = []
    # Remove the user from any group where it belonged:
    groups_dir = sops_groups_folder(flake_dir)
    if groups_dir.exists():
        for group in groups_dir.iterdir():
            group_folder = groups_dir / group
            if not group_folder.is_dir():
                continue
            memberships = group_folder / "users"
            if not (memberships / name).exists():
                continue
            log.info(f"Removing user {name} from group {group}")
            updated_paths.extend(
                groups.remove_member(flake_dir, group.name, groups.users_folder, name),
            )
    # Remove the user's key:
    updated_paths.extend(remove_object(sops_users_folder(flake_dir), name))
    # Remove the user from any secret where it was used:
    filter_user_secrets = get_secrets_filter_for_user(flake_dir, name)
    updated_paths.extend(update_secrets(flake_dir, filter_user_secrets))
    commit_files(updated_paths, flake_dir, f"Remove user {name}")


def get_user(flake_dir: Path, name: str) -> set[sops.SopsKey]:
    keys = read_keys(sops_users_folder(flake_dir) / name)
    return {
        sops.SopsKey(key.pubkey, name, key.key_type, source=key.source) for key in keys
    }


def list_users(flake_dir: Path) -> list[str]:
    path = sops_users_folder(flake_dir)

    def validate(name: str) -> bool:
        return (
            VALID_USER_NAME.match(name) is not None
            and (path / name / "key.json").exists()
        )

    return list_objects(path, validate)


def add_secret(
    flake_dir: Path,
    user: str,
    secret: str,
    age_plugins: list[str] | None,
) -> None:
    updated_paths = secrets.allow_member(
        secrets.users_folder(sops_secrets_folder(flake_dir) / secret),
        sops_users_folder(flake_dir),
        user,
        age_plugins=age_plugins,
    )
    commit_files(
        updated_paths,
        flake_dir,
        f"Add {user} to secret",
    )


def remove_secret(
    flake_dir: Path,
    user: str,
    secret: str,
    age_plugins: list[str] | None,
) -> None:
    updated_paths = secrets.disallow_member(
        secrets.users_folder(sops_secrets_folder(flake_dir) / secret),
        user,
        age_plugins,
    )
    commit_files(
        updated_paths,
        flake_dir,
        f"Remove {user} from secret",
    )


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    lst = list_users(flake.path)
    if len(lst) > 0:
        print("\n".join(lst))


def add_user_key(
    flake_dir: Path,
    name: str,
    keys: Iterable[sops.SopsKey],
) -> None:
    path = sops_users_folder(flake_dir) / name

    append_keys(path, keys)
    updated_paths = [path]

    filter_user_secrets = get_secrets_filter_for_user(flake_dir, name)
    updated_paths.extend(update_secrets(flake_dir, filter_user_secrets))
    commit_files(
        updated_paths,
        flake_dir,
        f"Add key(s) for user {name} to secrets",
    )


def remove_user_key(
    flake_dir: Path,
    name: str,
    keys: Iterable[sops.SopsKey],
) -> None:
    path = sops_users_folder(flake_dir) / name

    remove_keys(path, keys)
    updated_paths = [path]

    filter_user_secrets = get_secrets_filter_for_user(flake_dir, name)
    updated_paths.extend(update_secrets(flake_dir, filter_user_secrets))
    commit_files(
        updated_paths,
        flake_dir,
        f"Remove key(s) for user {name} from secrets",
    )


def _key_args(args: argparse.Namespace) -> Iterable[sops.SopsKey]:
    age_keys = args.age_key or []
    pgp_keys = args.pgp_key or []

    key_count = len(age_keys) + len(pgp_keys)
    if args.agekey:
        key_count += 1

    if key_count == 0:
        err_msg = (
            "Please provide at least one key through `--pgp-key`, "
            "`--age-key`, or as a positional (age key) argument."
        )
        raise ClanError(err_msg)

    age_keys = [
        sops.SopsKey(key, "", sops.KeyType.AGE, source="cmdline") for key in age_keys
    ]
    if args.agekey:
        age_keys.append(
            sops.SopsKey(args.agekey, "", sops.KeyType.AGE, source="cmdline"),
        )

    pgp_keys = [
        sops.SopsKey(key, "", sops.KeyType.PGP, source="cmdline") for key in pgp_keys
    ]

    return age_keys + pgp_keys


def add_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)

    add_user(flake.path, args.user, _key_args(args), args.force)


def get_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    keys = get_user(flake.path, args.user)
    json.dump([key.as_dict() for key in keys], sys.stdout, indent=2, sort_keys=True)


def remove_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    remove_user(flake.path, args.user)


def add_secret_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    add_secret(
        flake.path,
        args.user,
        args.secret,
        age_plugins=load_age_plugins(flake),
    )


def remove_secret_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    remove_secret(
        flake.path,
        args.user,
        args.secret,
        age_plugins=load_age_plugins(flake),
    )


def add_key_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)

    add_user_key(flake.path, args.user, _key_args(args))


def remove_key_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)

    remove_user_key(flake.path, args.user, _key_args(args))


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
        "-f",
        "--force",
        help="overwrite existing user",
        action="store_true",
    )
    add_parser.add_argument("user", help="the name of the user", type=user_name_type)
    _add_key_flags(add_parser)
    add_parser.set_defaults(func=add_command)

    get_parser = subparser.add_parser("get", help="get a user public key")
    get_user_action = get_parser.add_argument(
        "user",
        help="the name of the user",
        type=user_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_users,
    )

    add_dynamic_completer(get_user_action, complete_users)
    get_parser.set_defaults(func=get_command)

    remove_parser = subparser.add_parser("remove", help="remove a user")
    remove_user_action = remove_parser.add_argument(
        "user",
        help="the name of the user",
        type=user_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_users,
    )

    add_dynamic_completer(remove_user_action, complete_users)
    remove_parser.set_defaults(func=remove_command)

    add_secret_parser = subparser.add_parser(
        "add-secret",
        help="allow a user to access a secret",
    )
    add_secret_user_action = add_secret_parser.add_argument(
        "user",
        help="the name of the user",
        type=user_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_secrets,
        complete_users,
    )

    add_dynamic_completer(add_secret_user_action, complete_users)
    add_secrets_action = add_secret_parser.add_argument(
        "secret",
        help="the name of the secret",
        type=secret_name_type,
    )
    add_dynamic_completer(add_secrets_action, complete_secrets)
    add_secret_parser.set_defaults(func=add_secret_command)

    remove_secret_parser = subparser.add_parser(
        "remove-secret",
        help="remove a user's access to a secret",
    )
    remove_secret_user_action = remove_secret_parser.add_argument(
        "user",
        help="the name of the group",
        type=user_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_secrets,
        complete_users,
    )

    add_dynamic_completer(remove_secret_user_action, complete_users)
    remove_secrets_action = remove_secret_parser.add_argument(
        "secret",
        help="the name of the secret",
        type=secret_name_type,
    )
    add_dynamic_completer(remove_secrets_action, complete_secrets)
    remove_secret_parser.set_defaults(func=remove_secret_command)

    add_key_parser = subparser.add_parser(
        "add-key",
        help="add one or more keys for a user",
    )
    add_key_user_action = add_key_parser.add_argument(
        "user",
        help="the name of the user",
        type=user_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_users,
    )

    add_dynamic_completer(add_key_user_action, complete_users)
    _add_key_flags(add_key_parser)
    add_key_parser.set_defaults(func=add_key_command)

    remove_key_parser = subparser.add_parser(
        "remove-key",
        help="remove one or more keys for a user",
    )
    remove_key_user_action = remove_key_parser.add_argument(
        "user",
        help="the name of the user",
        type=user_name_type,
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_users,
    )

    add_dynamic_completer(remove_key_user_action, complete_users)
    _add_key_flags(remove_key_parser)
    remove_key_parser.set_defaults(func=remove_key_command)


def _add_key_flags(parser: argparse.ArgumentParser) -> None:
    key_type = parser.add_mutually_exclusive_group(required=True)
    key_type.add_argument(
        "agekey",
        help="public or private age key for a user. "
        "Execute 'clan secrets key --help' on how to retrieve a key. "
        "To fetch an age key from an SSH host key: ssh-keyscan <domain_name> | nix shell nixpkgs#ssh-to-age -c ssh-to-age",
        type=public_or_private_age_key_type,
        nargs="?",
    )
    key_type.add_argument(
        "--age-key",
        help="public or private age key for a user. "
        "Execute 'clan secrets key --help' on how to retrieve a key. "
        "To fetch an age key from an SSH host key: ssh-keyscan <domain_name> | nix shell nixpkgs#ssh-to-age -c ssh-to-age",
        type=public_or_private_age_key_type,
        action="append",
    )
    key_type.add_argument(
        "--pgp-key",
        help=(
            "public PGP encryption key for a user. "
            # Use --fingerprint --fingerprint to get fingerprints for subkeys:
            "Execute `gpg -k --fingerprint --fingerprint` and remove spaces to get it."
        ),
        action="append",
    )
