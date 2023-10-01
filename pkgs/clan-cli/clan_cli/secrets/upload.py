import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from ..dirs import get_clan_flake_toplevel
from ..errors import ClanError
from ..nix import nix_build, nix_config, nix_shell
from ..ssh import parse_deployment_address

log = logging.getLogger(__name__)


def build_upload_script(machine: str, clan_dir: Path) -> str:
    config = nix_config()
    system = config["system"]

    cmd = nix_build(
        [
            f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.system.clan.uploadSecrets'
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise ClanError(
            f"failed to upload secrets:\n{shlex.join(cmd)}\nexited with {proc.returncode}"
        )

    return proc.stdout.strip()


def get_deployment_info(machine: str, clan_dir: Path) -> dict:
    config = nix_config()
    system = config["system"]

    cmd = nix_build(
        [
            f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.system.clan.deployment.file'
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise ClanError(
            f"failed to get deploymentAddress:\n{shlex.join(cmd)}\nexited with {proc.returncode}"
        )

    return json.load(open(proc.stdout.strip()))


def get_decrypted_secrets(
    flake_attr: str, clan_dir: Path, target_directory: Path
) -> None:
    env = os.environ.copy()
    env["CLAN_DIR"] = str(clan_dir)
    env["PYTHONPATH"] = ":".join(sys.path)  # TODO do this in the clanCore module
    print(f"uploading secrets... {flake_attr}")
    with TemporaryDirectory() as tempdir_:
        tempdir = Path(tempdir_)
        env["SECRETS_DIR"] = str(tempdir)
        proc = subprocess.run(
            [flake_attr],
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )

        if proc.returncode != 0:
            log.error("Stdout: %s", proc.stdout)
            log.error("Stderr: %s", proc.stderr)
            raise ClanError("failed to upload secrets")

        h = parse_deployment_address(flake_attr, target)
        ssh_cmd = h.ssh_cmd()
        subprocess.run(
            nix_shell(
                ["rsync"],
                [
                    "rsync",
                    "-e",
                    " ".join(["ssh"] + ssh_cmd[2:]),
                    "-az",
                    "--delete",
                    f"{str(tempdir)}/",
                    f"{h.user}@{h.host}:{target_directory}/",
                ],
            ),
            check=True,
        )


def upload_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel()
    deployment_info = get_deployment_info(machine, clan_dir)
    address = deployment_info.get("deploymentAddress", "")
    secrets_upload_directory = deployment_info.get("secretsUploadDirectory", "")
    run_upload_secrets(
        build_upload_script(machine, clan_dir),
        clan_dir,
        address,
        secrets_upload_directory,
    )


def upload_command(args: argparse.Namespace) -> None:
    upload_secrets(args.machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    parser.set_defaults(func=upload_command)
