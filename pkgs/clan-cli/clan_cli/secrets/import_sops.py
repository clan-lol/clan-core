import argparse
import json
import subprocess
import sys
from pathlib import Path

from ..errors import ClanError
from ..nix import nix_shell
from .secrets import encrypt_secret


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
            if not isinstance(v, str):
                print(
                    f"WARNING: {k} is not a string but {type(v)}, skipping",
                    file=sys.stderr,
                )
            encrypt_secret(k, v)


def register_import_sops_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "sops_file",
        type=str,
        help="the sops file to import (- for stdin)",
    )
    parser.add_argument(
        "input_type",
        type=str,
        help="the input type of the sops file (yaml, json, ...)",
    )
    parser.set_defaults(func=import_sops)
