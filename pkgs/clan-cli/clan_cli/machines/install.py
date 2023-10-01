import argparse
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_build, nix_config, nix_shell
from ..secrets.generate import run_generate_secrets
from ..secrets.upload import get_decrypted_secrets
from ..ssh import Host, parse_deployment_address


def install_nixos(h: Host, clan_dir: Path) -> None:
    target_host = f"{h.user or 'root'}@{h.host}"

    flake_attr = h.meta.get("flake_attr", "")

    run_generate_secrets(h.meta["generateSecrets"], clan_dir)

    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        get_decrypted_secrets(
            h.meta["uploadSecrets"],
            clan_dir,
            target_directory=tmpdir / h.meta["secretsUploadDirectory"].lstrip("/"),
        )

        subprocess.run(
            nix_shell(
                ["nixos-anywhere"],
                [
                    "nixos-anywhere",
                    "-f",
                    f"{clan_dir}#{flake_attr}",
                    "-t",
                    "--no-reboot",
                    "--extra-files",
                    str(tmpdir),
                    target_host,
                ],
            ),
            check=True,
        )


def install(args: argparse.Namespace) -> None:
    clan_dir = get_clan_flake_toplevel()
    config = nix_config()
    system = config["system"]
    json_file = subprocess.run(
        nix_build(
            [
                f'{clan_dir}#clanInternals.machines."{system}"."{args.machine}".config.system.clan.deployment.file'
            ]
        ),
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    ).stdout.strip()
    machine_json = json.loads(Path(json_file).read_text())
    host = parse_deployment_address(args.machine, args.target_host, machine_json)

    install_nixos(host, clan_dir)


def register_install_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    parser.add_argument(
        "target_host",
        type=str,
        help="ssh address to install to in the form of user@host:2222",
    )

    parser.set_defaults(func=install)
