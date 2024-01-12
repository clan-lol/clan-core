import logging
import os
import shlex
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from clan_cli.cmd import Log, run
from clan_cli.nix import nix_shell

from ..errors import ClanError
from .folders import sops_secrets_folder
from .machines import add_machine, has_machine
from .secrets import decrypt_secret, encrypt_secret, has_secret
from .sops import generate_private_key

log = logging.getLogger(__name__)


def generate_host_key(flake_dir: Path, machine_name: str) -> None:
    if has_machine(flake_dir, machine_name):
        return
    priv_key, pub_key = generate_private_key()
    encrypt_secret(
        flake_dir,
        sops_secrets_folder(flake_dir) / f"{machine_name}-age.key",
        priv_key,
    )
    add_machine(flake_dir, machine_name, pub_key, False)


def generate_secrets_group(
    flake_dir: Path,
    secret_group: str,
    machine_name: str,
    tempdir: Path,
    secret_options: dict[str, Any],
) -> None:
    clan_dir = flake_dir
    secrets = secret_options["secrets"]
    needs_regeneration = any(
        not has_secret(flake_dir, f"{machine_name}-{name}") for name in secrets
    ) or any(
        not (flake_dir / fact).exists() for fact in secret_options["facts"].values()
    )

    generator = secret_options["generator"]
    subdir = tempdir / secret_group
    if needs_regeneration:
        facts_dir = subdir / "facts"
        facts_dir.mkdir(parents=True)
        secrets_dir = subdir / "secrets"
        secrets_dir.mkdir(parents=True)

        text = f"""
set -euo pipefail
export facts={shlex.quote(str(facts_dir))}
export secrets={shlex.quote(str(secrets_dir))}
{generator}
        """
        cmd = nix_shell(["nixpkgs#bash"], ["bash", "-c", text])
        run(cmd, log=Log.BOTH)

        for name in secrets:
            secret_file = secrets_dir / name
            if not secret_file.is_file():
                msg = f"did not generate a file for '{name}' when running the following command:\n"
                msg += text
                raise ClanError(msg)
            encrypt_secret(
                flake_dir,
                sops_secrets_folder(flake_dir) / f"{machine_name}-{name}",
                secret_file.read_text(),
                add_machines=[machine_name],
            )
        for name, fact_path in secret_options["facts"].items():
            fact_file = facts_dir / name
            if not fact_file.is_file():
                msg = f"did not generate a file for '{name}' when running the following command:\n"
                msg += text
                raise ClanError(msg)
            fact_path = clan_dir / fact_path
            fact_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fact_file, fact_path)


# this is called by the sops.nix clan core module
def generate_secrets_from_nix(
    machine_name: str,
    secret_submodules: dict[str, Any],
) -> None:
    flake_dir = Path(os.environ["CLAN_DIR"])
    generate_host_key(flake_dir, machine_name)
    errors = {}
    log.debug("Generating secrets for machine %s and flake %s", machine_name, flake_dir)
    with TemporaryDirectory() as d:
        # if any of the secrets are missing, we regenerate all connected facts/secrets
        for secret_group, secret_options in secret_submodules.items():
            try:
                generate_secrets_group(
                    flake_dir, secret_group, machine_name, Path(d), secret_options
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
    machine_name: str,
) -> None:
    flake_dir = Path(os.environ["CLAN_DIR"])
    log.debug("Uploading secrets for machine %s and flake %s", machine_name, flake_dir)
    secret_name = f"{machine_name}-age.key"
    if not has_secret(
        flake_dir, secret_name
    ):  # skip uploading the secret, not managed by us
        return
    secret = decrypt_secret(flake_dir, secret_name)

    secrets_dir = Path(os.environ["SECRETS_DIR"])
    (secrets_dir / "key.txt").write_text(secret)
