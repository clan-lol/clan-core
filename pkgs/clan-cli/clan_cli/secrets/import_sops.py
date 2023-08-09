import argparse
import json
import subprocess
import sys
from pathlib import Path

from ..errors import ClanError
from ..nix import nix_shell
from .secrets import encrypt_secret, sops_secrets_folder


def import_sops(args: argparse.Namespace) -> None:
    file = Path(args.sops_file)
    file_type = file.suffix

    try:
        file.read_text()
    except OSError as e:
        raise ClanError(f"Could not read file {file}: {e}") from e
    if file_type == ".yaml":
        cmd = ["sops"]
        if args.input_type:
            cmd += ["--input-type", args.input_type]
        cmd += ["--output-type", "json", "--decrypt", args.sops_file]
        cmd = nix_shell(["sops"], cmd)
        try:
            res = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise ClanError(f"Could not import sops file {file}: {e}") from e
        secrets = json.loads(res.stdout)
        for k, v in secrets.items():
            k = args.prefix + k
            if not isinstance(v, str):
                print(
                    f"WARNING: {k} is not a string but {type(v)}, skipping",
                    file=sys.stderr,
                )
                continue
            if (sops_secrets_folder() / k).exists():
                print(
                    f"WARNING: {k} already exists, skipping",
                    file=sys.stderr,
                )
                continue
            encrypt_secret(
                sops_secrets_folder() / k,
                v,
                add_groups=args.group,
                add_machines=args.machine,
                add_users=args.user,
            )


def register_import_sops_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input-type",
        type=str,
        default=None,
        help="the input type of the sops file (yaml, json, ...). If not specified, it will be guessed from the file extension",
    )
    parser.add_argument(
        "--group",
        type=str,
        action="append",
        default=[],
        help="the group to import the secrets to",
    )
    parser.add_argument(
        "--machine",
        type=str,
        action="append",
        default=[],
        help="the machine to import the secrets to",
    )
    parser.add_argument(
        "--user",
        type=str,
        action="append",
        default=[],
        help="the user to import the secrets to",
    )
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
