import argparse
import json
import logging
import shlex
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from ..errors import ClanError
from ..machines.machines import Machine
from ..nix import nix_build, nix_config, nix_shell

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


def upload_secrets(machine: Machine) -> None:
    with TemporaryDirectory() as tempdir_:
        tempdir = Path(tempdir_)
        machine.run_upload_secrets(tempdir)
        host = machine.host

        ssh_cmd = host.ssh_cmd()
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
                    f"{host.user}@{host.host}:{machine.secrets_upload_directory}/",
                ],
            ),
            check=True,
        )


def upload_command(args: argparse.Namespace) -> None:
    machine = Machine(args.machine)
    upload_secrets(machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    parser.set_defaults(func=upload_command)
