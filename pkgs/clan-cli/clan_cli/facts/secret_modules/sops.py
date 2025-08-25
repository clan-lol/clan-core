from pathlib import Path
from typing import override

from clan_lib.machines.machines import Machine
from clan_lib.ssh.host import Host

from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.secrets.machines import add_machine, has_machine
from clan_cli.secrets.secrets import decrypt_secret, encrypt_secret, has_secret
from clan_cli.secrets.sops import generate_private_key, load_age_plugins

from . import SecretStoreBase


class SecretStore(SecretStoreBase):
    def __init__(self, machine: Machine) -> None:
        self.machine = machine

        # no need to generate keys if we don't manage secrets
        if not hasattr(self.machine, "facts_data"):
            return

        if not self.machine.facts_data:
            return

        if has_machine(self.machine.flake_dir, self.machine.name):
            return
        priv_key, pub_key = generate_private_key()
        encrypt_secret(
            self.machine.flake_dir,
            sops_secrets_folder(self.machine.flake_dir)
            / f"{self.machine.name}-age.key",
            priv_key,
            add_groups=self.machine.select("config.clan.core.sops.defaultGroups"),
            age_plugins=load_age_plugins(self.machine.flake),
        )
        add_machine(self.machine.flake_dir, self.machine.name, pub_key, False)

    def set(
        self,
        service: str,
        name: str,
        value: bytes,
        groups: list[str],
    ) -> Path | None:
        del service  # Unused but kept for API compatibility
        path = (
            sops_secrets_folder(self.machine.flake_dir) / f"{self.machine.name}-{name}"
        )
        encrypt_secret(
            self.machine.flake_dir,
            path,
            value,
            add_machines=[self.machine.name],
            add_groups=groups,
            age_plugins=load_age_plugins(self.machine.flake),
        )
        return path

    def get(self, service: str, name: str) -> bytes:
        del service  # Unused but kept for API compatibility
        return decrypt_secret(
            sops_secrets_folder(self.machine.flake_dir) / f"{self.machine.name}-{name}",
            age_plugins=load_age_plugins(self.machine.flake),
        ).encode("utf-8")

    def exists(self, service: str, name: str) -> bool:
        del service  # Unused but kept for API compatibility
        return has_secret(
            sops_secrets_folder(self.machine.flake_dir) / f"{self.machine.name}-{name}",
        )

    @override
    def needs_upload(self, host: Host) -> bool:
        return False

    # We rely now on the vars backend to upload the age key
    def upload(self, output_dir: Path) -> None:
        pass
