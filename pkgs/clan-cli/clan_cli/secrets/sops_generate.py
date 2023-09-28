import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from clan_cli.nix import nix_shell

from ..dirs import get_clan_flake_toplevel
from ..errors import ClanError
from ..ssh import parse_deployment_address
from .folders import sops_secrets_folder
from .machines import add_machine, has_machine
from .secrets import decrypt_secret, encrypt_secret, has_secret
from .sops import generate_private_key


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
export facts={shlex.quote(str(facts_dir))}
export secrets={shlex.quote(str(secrets_dir))}
{generator}
        """
        try:
            cmd = nix_shell(["bash"], ["bash", "-c", text])
            subprocess.run(cmd, check=True)
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


# this is called by the sops.nix clan core module
def upload_age_key_from_nix(
    machine_name: str, deployment_address: str, age_key_file: str
) -> None:
    secret_name = f"{machine_name}-age.key"
    if not has_secret(secret_name):  # skip uploading the secret, not managed by us
        return
    secret = decrypt_secret(secret_name)

    h = parse_deployment_address(machine_name, deployment_address)
    path = Path(age_key_file)

    proc = h.run(
        [
            "bash",
            "-c",
            'mkdir -p "$0" && echo -n "$1" > "$2"',
            str(path.parent),
            secret,
            age_key_file,
        ],
        check=False,
    )
    if proc.returncode != 0:
        print(f"failed to upload age key to {deployment_address}")
        sys.exit(1)
