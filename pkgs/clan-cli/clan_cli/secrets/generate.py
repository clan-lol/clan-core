import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel, module_root
from ..nix import nix_build, nix_config
from .folders import sops_secrets_folder
from .machines import add_machine, has_machine
from .secrets import encrypt_secret, has_secret
from .sops import generate_private_key


def generate_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix().strip()
    env = os.environ.copy()
    env["CLAN_DIR"] = clan_dir
    env["PYTHONPATH"] = str(module_root().parent)
    config = nix_config()
    system = config["system"]

    cmd = nix_build(
        [
            f'path:{clan_dir}#nixosConfigurations."{machine}".config.system.clan.{system}.generateSecrets'
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise ClanError(
            f"failed to generate secrets:\n{shlex.join(cmd)}\nexited with {proc.returncode}"
        )

    secret_generator_script = proc.stdout.strip()
    print(secret_generator_script)
    secret_generator = subprocess.run(
        [secret_generator_script],
        env=env,
    )

    if secret_generator.returncode != 0:
        raise ClanError("failed to generate secrets")
    else:
        print("successfully generated secrets")


def generate_host_key(machine_name: str) -> None:
    if has_machine(machine_name):
        return
    priv_key, pub_key = generate_private_key()
    encrypt_secret(sops_secrets_folder() / f"{machine_name}-age.key", priv_key)
    add_machine(machine_name, pub_key, False)


def generate_secrets_group(
    secret_group: str, machine_name: str, tempdir: Path, secret_options: dict[str, Any]
) -> None:
    clan_dir = get_clan_flake_toplevel()
    secrets = secret_options["secrets"]
    needs_regeneration = any(
        not has_secret(f"{machine_name}-{secret['name']}")
        for secret in secrets.values()
    )
    generator = secret_options["generator"]
    subdir = tempdir / secret_group
    if needs_regeneration:
        facts_dir = subdir / "facts"
        facts_dir.mkdir(parents=True)
        secrets_dir = subdir / "secrets"
        secrets_dir.mkdir(parents=True)

        text = f"""\
set -euo pipefail
facts={shlex.quote(str(facts_dir))}
secrets={shlex.quote(str(secrets_dir))}
{generator}
        """
        try:
            subprocess.run(["bash", "-c", text], check=True)
        except subprocess.CalledProcessError:
            msg = "failed to the following command:\n"
            msg += text
            raise ClanError(msg)
        for secret in secrets.values():
            secret_file = secrets_dir / secret["name"]
            if not secret_file.is_file():
                msg = f"did not generate a file for '{secret['name']}' when running the following command:\n"
                msg += text
                raise ClanError(msg)
            encrypt_secret(
                sops_secrets_folder() / f"{machine_name}-{secret['name']}",
                secret_file.read_text(),
            )
        for fact in secret_options["facts"].values():
            fact_file = facts_dir / fact["name"]
            if not fact_file.is_file():
                msg = f"did not generate a file for '{fact['name']}' when running the following command:\n"
                msg += text
                raise ClanError(msg)
            fact_path = clan_dir.joinpath(fact["path"])
            fact_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fact_file, fact_path)


# this is called by the sops.nix clan core module
def generate_secrets_from_nix(
    machine_name: str,
    secret_submodules: dict[str, Any],
) -> None:
    generate_host_key(machine_name)
    errors = {}
    with TemporaryDirectory() as d:
        # if any of the secrets are missing, we regenerate all connected facts/secrets
        for secret_group, secret_options in secret_submodules.items():
            try:
                generate_secrets_group(
                    secret_group, machine_name, Path(d), secret_options
                )
            except ClanError as e:
                errors[secret_group] = e
    for secret_group, error in errors.items():
        print(f"failed to generate secrets for {machine_name}/{secret_group}:")
        print(error, file=sys.stderr)
    if len(errors) > 0:
        sys.exit(1)


def generate_command(args: argparse.Namespace) -> None:
    generate_secrets(args.machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
