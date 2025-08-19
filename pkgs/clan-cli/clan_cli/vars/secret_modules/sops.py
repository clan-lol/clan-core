import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from clan_cli.secrets import sops
from clan_cli.secrets.folders import (
    sops_groups_folder,
    sops_machines_folder,
    sops_secrets_folder,
    sops_users_folder,
)
from clan_cli.secrets.machines import add_machine, add_secret, has_machine
from clan_cli.secrets.secrets import (
    allow_member,
    collect_keys_for_path,
    decrypt_secret,
    encrypt_secret,
    groups_folder,
    has_secret,
)
from clan_cli.secrets.sops import load_age_plugins
from clan_cli.vars._types import StoreBase
from clan_cli.vars.generator import Generator
from clan_cli.vars.var import Var
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host
from clan_lib.ssh.upload import upload


@dataclass
class SopsKey:
    pubkey: str
    username: str


class MissingKeyError(ClanError):
    def __init__(self) -> None:
        msg = "Cannot find admin keys for current $USER on this computer. Please initialize admin keys once with 'clan vars keygen'"
        super().__init__(msg)


class SecretStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)

    def ensure_machine_key(self, machine: str) -> None:
        """Ensure machine has sops keys initialized."""
        # no need to generate keys if we don't manage secrets
        from clan_cli.vars.generator import Generator

        vars_generators = Generator.get_machine_generators(machine, self.flake)
        if not vars_generators:
            return
        has_secrets = False
        for generator in vars_generators:
            for file in generator.files:
                if file.secret:
                    has_secrets = True
        if not has_secrets:
            return

        if has_machine(self.flake.path, machine):
            return
        priv_key, pub_key = sops.generate_private_key()
        encrypt_secret(
            self.flake.path,
            sops_secrets_folder(self.flake.path) / f"{machine}-age.key",
            priv_key,
            add_groups=self.flake.select_machine(
                machine, "config.clan.core.sops.defaultGroups"
            ),
            age_plugins=load_age_plugins(self.flake),
        )
        add_machine(self.flake.path, machine, pub_key, False)

    @property
    def store_name(self) -> str:
        return "sops"

    def user_has_access(
        self, user: str, generator: Generator, secret_name: str
    ) -> bool:
        key_dir = sops_users_folder(self.flake.path) / user
        return self.key_has_access(key_dir, generator, secret_name)

    def machine_has_access(self, generator: Generator, secret_name: str) -> bool:
        machine = self.get_machine(generator)
        self.ensure_machine_key(machine)
        key_dir = sops_machines_folder(self.flake.path) / machine
        return self.key_has_access(key_dir, generator, secret_name)

    def key_has_access(
        self, key_dir: Path, generator: Generator, secret_name: str
    ) -> bool:
        secret_path = self.secret_path(generator, secret_name)
        recipient = sops.SopsKey.load_dir(key_dir)
        recipients = sops.get_recipients(secret_path)
        return len(recipient.intersection(recipients)) > 0

    def secret_path(self, generator: Generator, secret_name: str) -> Path:
        return self.directory(generator, secret_name)

    @override
    def health_check(
        self,
        machine: str,
        generators: list[Generator] | None = None,
        file_name: str | None = None,
    ) -> str | None:
        """
        Check if SOPS secrets need to be re-encrypted due to recipient changes.

        This method verifies that all secrets are properly encrypted with the current
        set of recipient keys. It detects when new users or machines have been added
        to the clan but secrets haven't been re-encrypted to grant them access.

        Args:
            machine: The name of the machine to check secrets for
            generators: List of generators to check. If None, checks all generators for the machine
            file_name: Optional specific file to check. If provided, only checks that file

        Returns:
            str | None: A message describing which secrets need updating, or None if all secrets are up-to-date

        Raises:
            ClanError: If the specified file_name is not found
        """

        if generators is None:
            from clan_cli.vars.generator import Generator

            generators = Generator.get_machine_generators(machine, self.flake)
        file_found = False
        outdated = []
        for generator in generators:
            for file in generator.files:
                # if we check only a single file, continue on all the other ones
                if file_name:
                    if file.name == file_name:
                        file_found = True
                    else:
                        continue
                if file.secret and self.exists(generator, file.name):
                    if file.deploy:
                        self.ensure_machine_has_access(generator, file.name)
                    needs_update, msg = self.needs_fix(generator, file.name)
                    if needs_update:
                        outdated.append((generator.name, file.name, msg))
        if file_name and not file_found:
            msg = f"file {file_name} was not found"
            raise ClanError(msg)
        if outdated:
            msg = (
                "The local state of some secret vars is inconsistent and needs to be updated.\n"
                f"Run 'clan vars fix {machine}' to apply the necessary changes."
                "Problems to fix:\n"
                "\n".join(o[2] for o in outdated if o[2])
            )
            return msg
        return None

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
    ) -> Path | None:
        machine = self.get_machine(generator)
        self.ensure_machine_key(machine)
        secret_folder = self.secret_path(generator, var.name)
        # create directory if it doesn't exist
        secret_folder.mkdir(parents=True, exist_ok=True)
        # initialize the secret
        encrypt_secret(
            self.flake.path,
            secret_folder,
            value,
            add_machines=[machine] if var.deploy else [],
            add_groups=self.flake.select_machine(
                machine, "config.clan.core.sops.defaultGroups"
            ),
            git_commit=False,
            age_plugins=load_age_plugins(self.flake),
        )
        return secret_folder

    def get(self, generator: Generator, name: str) -> bytes:
        return decrypt_secret(
            self.secret_path(generator, name),
            age_plugins=load_age_plugins(self.flake),
        ).encode("utf-8")

    def delete(self, generator: "Generator", name: str) -> Iterable[Path]:
        secret_dir = self.directory(generator, name)
        shutil.rmtree(secret_dir)
        return [secret_dir]

    def delete_store(self, machine: str) -> Iterable[Path]:
        flake_root = self.flake.path
        store_folder = flake_root / "vars/per-machine" / machine
        if not store_folder.exists():
            return []
        shutil.rmtree(store_folder)
        return [store_folder]

    def populate_dir(self, machine: str, output_dir: Path, phases: list[str]) -> None:
        from clan_cli.vars.generator import Generator

        vars_generators = Generator.get_machine_generators(machine, self.flake)
        if "users" in phases or "services" in phases:
            key_name = f"{machine}-age.key"
            if not has_secret(sops_secrets_folder(self.flake.path) / key_name):
                # skip uploading the secret, not managed by us
                return
            key = decrypt_secret(
                sops_secrets_folder(self.flake.path) / key_name,
                age_plugins=load_age_plugins(self.flake),
            )
            (output_dir / "key.txt").touch(mode=0o600)
            (output_dir / "key.txt").write_text(key)

        if "activation" in phases:
            for generator in vars_generators:
                for file in generator.files:
                    if file.needed_for == "activation":
                        target_path = (
                            output_dir / "activation" / generator.name / file.name
                        )
                        target_path.parent.mkdir(
                            parents=True,
                            exist_ok=True,
                        )
                        # chmod after in case it doesn't have u+w
                        target_path.touch(mode=0o600)
                        target_path.write_bytes(self.get(generator, file.name))
                        target_path.chmod(file.mode)

        if "partitioning" in phases:
            for generator in vars_generators:
                for file in generator.files:
                    if file.needed_for == "partitioning":
                        target_path = output_dir / generator.name / file.name
                        target_path.parent.mkdir(
                            parents=True,
                            exist_ok=True,
                        )
                        # chmod after in case it doesn't have u+w
                        target_path.touch(mode=0o600)
                        target_path.write_bytes(self.get(generator, file.name))
                        target_path.chmod(file.mode)

    @override
    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        if "partitioning" in phases:
            msg = "Cannot upload partitioning secrets"
            raise NotImplementedError(msg)
        with TemporaryDirectory(prefix="sops-upload-") as _tempdir:
            sops_upload_dir = Path(_tempdir).resolve()
            self.populate_dir(machine, sops_upload_dir, phases)
            upload(host, sops_upload_dir, Path("/var/lib/sops-nix"))

    def exists(self, generator: Generator, name: str) -> bool:
        secret_folder = self.secret_path(generator, name)
        return (secret_folder / "secret").exists()

    def ensure_machine_has_access(self, generator: Generator, name: str) -> None:
        machine = self.get_machine(generator)
        if self.machine_has_access(generator, name):
            return
        secret_folder = self.secret_path(generator, name)
        add_secret(
            self.flake.path,
            machine,
            secret_folder,
            age_plugins=load_age_plugins(self.flake),
        )

    def collect_keys_for_secret(self, machine: str, path: Path) -> set[sops.SopsKey]:
        from clan_cli.secrets.secrets import (
            collect_keys_for_path,
            collect_keys_for_type,
        )

        keys = collect_keys_for_path(path)
        for group in self.flake.select_machine(
            machine, "config.clan.core.sops.defaultGroups"
        ):
            keys.update(
                collect_keys_for_type(
                    self.flake.path / "sops" / "groups" / group / "machines"
                )
            )
            keys.update(
                collect_keys_for_type(
                    self.flake.path / "sops" / "groups" / group / "users"
                )
            )

        return keys

    def needs_fix(self, generator: Generator, name: str) -> tuple[bool, str | None]:
        machine = self.get_machine(generator)
        secret_path = self.secret_path(generator, name)
        current_recipients = sops.get_recipients(secret_path)
        wanted_recipients = self.collect_keys_for_secret(machine, secret_path)
        needs_update = current_recipients != wanted_recipients
        recipients_to_add = wanted_recipients - current_recipients
        var_id = f"{generator.name}/{name}"
        msg = (
            f"One or more recipient keys were added to secret{' shared' if generator.share else ''} var '{var_id}', but it was never re-encrypted.\n"
            f"This could have been a malicious actor trying to add their keys, please investigate.\n"
            f"Added keys: {', '.join(f'{r.key_type.name}:{r.pubkey}' for r in recipients_to_add)}\n"
            f"If this is intended, run 'clan vars fix {machine}' to re-encrypt the secret."
        )
        return needs_update, msg

    @override
    def fix(
        self,
        machine: str,
        generators: list[Generator] | None = None,
        file_name: str | None = None,
    ) -> None:
        """
        Fix sops secrets by re-encrypting them with the current set of recipient keys.

        This method updates secrets when recipients have changed (e.g., new admin users
        were added to the clan). It ensures all authorized recipients have access to the
        secrets and removes access from any removed recipients.

        Args:
            machine: The name of the machine to fix secrets for
            generators: List of generators to fix. If None, fixes all generators for the machine
            file_name: Optional specific file to fix. If provided, only fixes that file

        Raises:
            ClanError: If the specified file_name is not found
        """
        from clan_cli.secrets.secrets import update_keys

        if generators is None:
            from clan_cli.vars.generator import Generator

            generators = Generator.get_machine_generators(machine, self.flake)
        file_found = False
        for generator in generators:
            for file in generator.files:
                # if we check only a single file, continue on all the other ones
                if file_name:
                    if file.name == file_name:
                        file_found = True
                    else:
                        continue
                if not file.secret:
                    continue

                secret_path = self.secret_path(generator, file.name)

                age_plugins = load_age_plugins(self.flake)

                gen_machine = self.get_machine(generator)
                for group in self.flake.select_machine(
                    gen_machine, "config.clan.core.sops.defaultGroups"
                ):
                    allow_member(
                        groups_folder(secret_path),
                        sops_groups_folder(self.flake.path),
                        group,
                        # we just want to create missing symlinks, we call update_keys below:
                        do_update_keys=False,
                        age_plugins=age_plugins,
                    )

                update_keys(
                    secret_path,
                    collect_keys_for_path(secret_path),
                    age_plugins=age_plugins,
                )
        if file_name and not file_found:
            msg = f"file {file_name} was not found"
            raise ClanError(msg)
