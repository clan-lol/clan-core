import argparse
import json
import sys
from pathlib import Path

from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError
from clan_lib.nix import nix_shell

from clan_cli.secrets.sops import load_age_plugins

from .secrets import encrypt_secret, sops_secrets_folder


def import_sops(args: argparse.Namespace) -> None:
    file = Path(args.sops_file)
    file_type = file.suffix

    try:
        file.read_text()
    except OSError as e:
        msg = f"Could not read file {file}: {e}"
        raise ClanError(msg) from e
    if file_type == ".yaml":
        cmd = ["sops"]
        if args.input_type:
            cmd += ["--input-type", args.input_type]
        cmd += ["--output-type", "json", "--decrypt", args.sops_file]
        cmd = nix_shell(["sops", "gnupg"], cmd)

        res = run(cmd, RunOpts(error_msg=f"Could not import sops file {file}"))
        secrets = json.loads(res.stdout)
        for k, v in secrets.items():
            secret_name = args.prefix + k
            if not isinstance(v, str):
                print(
                    f"WARNING: {secret_name} is not a string but {type(v)}, skipping",
                    file=sys.stderr,
                )
                continue
            if (sops_secrets_folder(args.flake.path) / secret_name / "secret").exists():
                print(
                    f"WARNING: {secret_name} already exists, skipping",
                    file=sys.stderr,
                )
                continue
            encrypt_secret(
                args.flake.path,
                sops_secrets_folder(args.flake.path) / secret_name,
                v,
                add_groups=args.group,
                add_machines=args.machine,
                add_users=args.user,
                age_plugins=load_age_plugins(args.flake),
            )


def register_import_sops_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input-type",
        type=str,
        default=None,
        help="the input type of the sops file (yaml, json, ...). If not specified, it will be guessed from the file extension",
    )
    group_action = parser.add_argument(
        "--group",
        type=str,
        action="append",
        default=[],
        help="the group to import the secrets to",
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_groups,
    )

    add_dynamic_completer(group_action, complete_groups)
    machine_action = parser.add_argument(
        "--machine",
        type=str,
        action="append",
        default=[],
        help="the machine to import the secrets to",
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_machines,
    )

    add_dynamic_completer(machine_action, complete_machines)
    user_action = parser.add_argument(
        "--user",
        type=str,
        action="append",
        default=[],
        help="the user to import the secrets to",
    )
    from clan_cli.completions import (  # noqa: PLC0415
        add_dynamic_completer,
        complete_users,
    )

    add_dynamic_completer(user_action, complete_users)
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="the prefix to use for the secret names",
    )
    parser.add_argument(
        "sops_file",
        type=str,
        help="the sops file to import (- for stdin)",
    )

    parser.set_defaults(func=import_sops)
