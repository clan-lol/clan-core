import logging
import os
import shutil
from collections.abc import Iterable, Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import ClassVar, override

from clan_lib.cmd import Log, RunOpts
from clan_lib.cmd import run as cmd_run
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.flake import Flake
from clan_lib.git import commit_files
from clan_lib.nix import current_system
from clan_lib.nix_selectors import vars_age_secret_location, vars_settings_recipients
from clan_lib.ssh.host import Host
from clan_lib.ssh.upload import upload
from clan_lib.vars._types import (
    GeneratorId,
    GeneratorStore,
    PerExport,
    PerMachine,
    Shared,
    StoreBase,
)
from clan_lib.vars.var import Var

log = logging.getLogger(__name__)


class SecretStore(StoreBase):
    """Age-based secret store with target-side decryption.

    Secrets are encrypted to machine public keys. Each machine has its own
    age keypair. The machine's private key is encrypted to user keys, so
    rotating users only requires re-encrypting machine keys, not every secret.

    For shared vars, secrets are encrypted to all machines' public keys.
    """

    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)

    @property
    def store_name(self) -> str:
        return "age"

    # ── Path helpers ──────────────────────────────────────────────────────

    def secrets_dir(self) -> Path:
        return self.clan_dir / "secrets"

    def machine_key_dir(self, machine: str) -> Path:
        """Directory storing a machine's age keypair."""
        return self.secrets_dir() / "age-keys" / "machines" / machine

    def machine_pubkey_file(self, machine: str) -> Path:
        return self.machine_key_dir(machine) / "pub"

    def machine_encrypted_key_file(self, machine: str) -> Path:
        """Machine private key, encrypted to user keys."""
        return self.machine_key_dir(machine) / "key.age"

    def secret_path(self, generator: GeneratorId, name: str) -> Path:
        """Get the path to an encrypted secret file."""
        rel_path = self.rel_dir(generator, name)
        return self.secrets_dir() / "clan-vars" / rel_path / f"{name}.age"

    # ── User identity (for decrypting machine keys) ───────────────────────

    def get_recipients(self, machine: str) -> list[str]:
        """Get age user recipients for a machine from flake-level Nix config.

        These are the user keys that encrypt/decrypt machine private keys.
        """
        recipients_result = self.flake.select(
            vars_settings_recipients(),
        )

        # The ?recipients MAYBE selector wraps the result: {"recipients": {...}}
        recipients_config = recipients_result.get("recipients", {})

        recipients: list[str] = []

        if isinstance(recipients_config, dict):
            host_recipients_dict = recipients_config.get("hosts", {})
            if (
                isinstance(host_recipients_dict, dict)
                and machine in host_recipients_dict
            ):
                host_recipients = host_recipients_dict[machine]
                if isinstance(host_recipients, list):
                    recipients.extend(host_recipients)

            # Fall back to default recipients if no host-specific ones are set
            if not recipients:
                default_recipients = recipients_config.get("default", [])
                if isinstance(default_recipients, list):
                    recipients.extend(default_recipients)

        if not recipients:
            msg = (
                f"No age recipients configured for machine '{machine}'. "
                f"Please set vars.settings.recipients.hosts.{machine} or "
                f"vars.settings.recipients.default in your clan.nix"
            )
            raise ClanError(msg)

        return recipients

    # Well-known age identity file locations, checked in order as fallback
    _IDENTITY_SEARCH_PATHS: ClassVar[list[Path]] = [
        Path("~/.config/age/identities"),
        Path("~/.config/sops/age/keys.txt"),
        Path("~/.age/key.txt"),
    ]

    def get_identity(self) -> tuple[str | None, Path | None]:
        """Get the age identity for decrypting machine keys.

        Resolution order:
        1. AGE_KEY env var (inline private key)
        2. AGE_KEYFILE env var (path to identity file)
        3. Well-known file locations (~/.config/age/identities, etc.)

        Returns a tuple of (key_content, key_file_path).
        Either key_content is set (AGE_KEY) or key_file_path is set (AGE_KEYFILE).
        """
        age_key = os.environ.get("AGE_KEY")
        age_keyfile = os.environ.get("AGE_KEYFILE")

        if age_key:
            return (age_key, None)
        if age_keyfile:
            key_path = Path(age_keyfile)
            if not key_path.exists():
                msg = f"AGE_KEYFILE points to non-existent file: {age_keyfile}"
                raise ClanError(msg)
            return (None, key_path)

        # Try well-known locations
        for candidate in self._IDENTITY_SEARCH_PATHS:
            expanded = candidate.expanduser()
            if expanded.exists():
                log.debug("Using age identity from %s", expanded)
                return (None, expanded)

        search_paths = ", ".join(str(p) for p in self._IDENTITY_SEARCH_PATHS)
        msg = (
            "No age identity found. Set one of:\n"
            "  - AGE_KEY env var (inline private key)\n"
            "  - AGE_KEYFILE env var (path to identity file)\n"
            f"  - Or place an identity file at: {search_paths}"
        )
        raise ClanError(msg)

    # ── Machine key management ────────────────────────────────────────────

    def ensure_machine_key(self, machine: str) -> None:
        """Generate machine age keypair if it doesn't exist.

        The public key is stored in plaintext.
        The private key is encrypted to the user recipients for this machine.
        """
        if self.machine_pubkey_file(machine).exists():
            return

        key_dir = self.machine_key_dir(machine)
        key_dir.mkdir(parents=True, exist_ok=True)

        # Generate keypair
        try:
            result = cmd_run(
                ["age-keygen"],
                RunOpts(log=Log.NONE),
            )
        except ClanCmdError as e:
            msg = f"Failed to generate age keypair: {e.cmd.stderr}"
            raise ClanError(msg) from e

        # Parse output: age-keygen writes the private key to stdout,
        # with a comment line containing the public key
        private_key = result.stdout.encode()
        public_key = ""
        for line in result.stdout.splitlines():
            if line.startswith("# public key:"):
                public_key = line.split(":", 1)[1].strip()
                break

        if not public_key:
            msg = "Failed to parse public key from age-keygen output"
            raise ClanError(msg)

        # Store public key in plaintext
        pubkey_file = self.machine_pubkey_file(machine)
        pubkey_file.write_text(public_key)

        # Encrypt private key to user recipients
        encrypted_key_file = self.machine_encrypted_key_file(machine)
        recipients = self.get_recipients(machine)
        self._run_age_encrypt(
            private_key,
            recipients,
            encrypted_key_file,
        )
        self._write_recipients(encrypted_key_file, recipients)

        # Commit machine key files
        commit_files(
            [
                pubkey_file,
                encrypted_key_file,
                self._recipients_file(encrypted_key_file),
            ],
            self.flake.path,
            f"Add age machine key for '{machine}'",
        )

    def get_machine_pubkey(self, machine: str) -> str:
        """Read a machine's public key."""
        pubkey_file = self.machine_pubkey_file(machine)
        if not pubkey_file.exists():
            msg = (
                f"No machine key found for '{machine}'. "
                f"Run 'clan vars generate' to create one."
            )
            raise ClanError(msg)
        return pubkey_file.read_text().strip()

    def decrypt_machine_key(self, machine: str) -> bytes:
        """Decrypt a machine's private key using the user identity."""
        encrypted_key_file = self.machine_encrypted_key_file(machine)
        if not encrypted_key_file.exists():
            msg = f"No encrypted machine key found for '{machine}'."
            raise ClanError(msg)
        try:
            return self._run_age_decrypt(encrypted_key_file)
        except ClanError as e:
            msg = (
                f"Cannot decrypt machine key for '{machine}'. "
                f"Your age identity is not among the recipients of "
                f"'{encrypted_key_file}'. "
                f"A user whose key is listed in the recipients must run "
                f"'clan vars fix {machine}' to re-encrypt the machine key "
                f"for the current set of recipients."
            )
            raise ClanError(msg) from e

    def rekey_machine_key(self, machine: str) -> Path:
        """Re-encrypt machine private key to current user recipients.

        Used when user keys change. Returns the path to the re-encrypted key file.
        """
        # Decrypt with current user identity
        private_key = self.decrypt_machine_key(machine)

        # Re-encrypt to current user recipients
        recipients = self.get_recipients(machine)
        encrypted_key_file = self.machine_encrypted_key_file(machine)
        self._run_age_encrypt(private_key, recipients, encrypted_key_file)
        self._write_recipients(encrypted_key_file, recipients)

        log.info(f"Re-encrypted machine key for '{machine}'")
        return encrypted_key_file

    # ── Age encrypt/decrypt primitives ────────────────────────────────────

    @staticmethod
    def _recipients_file(age_file: Path) -> Path:
        """Return the path to the sidecar recipients file for an age file."""
        return age_file.with_suffix(".age.recipients")

    @staticmethod
    def _read_recipients(age_file: Path) -> list[str]:
        """Read the sorted recipient list from a sidecar file, or empty if missing."""
        recipients_file = SecretStore._recipients_file(age_file)
        if not recipients_file.exists():
            return []
        return sorted(recipients_file.read_text().strip().splitlines())

    @staticmethod
    def _write_recipients(age_file: Path, recipients: list[str]) -> Path:
        """Write sorted recipients to sidecar file. Returns the sidecar path."""
        recipients_file = SecretStore._recipients_file(age_file)
        recipients_file.write_text("\n".join(sorted(recipients)) + "\n")
        return recipients_file

    def _run_age_encrypt(
        self,
        value: bytes,
        recipients: list[str],
        output_file: Path,
    ) -> None:
        """Encrypt data with age to the specified recipients."""
        age_cmd = ["age", "--armor"]
        for recipient in recipients:
            age_cmd.extend(["-r", recipient])
        age_cmd.extend(["-o", str(output_file)])

        try:
            cmd_run(
                age_cmd,
                RunOpts(input=value, log=Log.NONE, sensitive_input=True),
            )
        except ClanCmdError as e:
            msg = f"Failed to encrypt secret: {e.cmd.stderr}"
            raise ClanError(msg) from e

    def _run_age_decrypt(self, encrypted_file: Path) -> bytes:
        """Decrypt an age-encrypted file using identity from environment."""
        key_content, key_file = self.get_identity()

        try:
            if key_content:
                age_cmd = ["age", "--decrypt", "-i", "-", str(encrypted_file)]
                result = cmd_run(
                    age_cmd,
                    RunOpts(
                        input=key_content.encode(), log=Log.NONE, sensitive_input=True
                    ),
                )
            else:
                age_cmd = ["age", "--decrypt", "-i", str(key_file), str(encrypted_file)]
                result = cmd_run(
                    age_cmd,
                    RunOpts(log=Log.NONE),
                )
        except ClanCmdError as e:
            msg = f"Failed to decrypt {encrypted_file}: {e.cmd.stderr}"
            raise ClanError(msg) from e

        return result.stdout.encode()

    def _run_age_decrypt_with_key(self, encrypted_file: Path, key_data: bytes) -> bytes:
        """Decrypt an age-encrypted file using a specific key (e.g. machine key)."""
        with NamedTemporaryFile(prefix="age-key-", suffix=".txt", delete=True) as tmp:
            tmp.write(key_data)
            tmp.flush()
            age_cmd = ["age", "--decrypt", "-i", tmp.name, str(encrypted_file)]
            try:
                result = cmd_run(
                    age_cmd,
                    RunOpts(log=Log.NONE),
                )
            except ClanCmdError as e:
                msg = f"Failed to decrypt {encrypted_file}: {e.cmd.stderr}"
                raise ClanError(msg) from e
        return result.stdout.encode()

    # ── StoreBase implementation ──────────────────────────────────────────

    def _set(
        self,
        generator: GeneratorStore,
        var: Var,
        value: bytes,
    ) -> list[Path]:
        """Encrypt and store a secret to the appropriate machine key(s)."""
        recipients: list[str] = []

        match generator.key.placement:
            case PerMachine(machine=machine):
                self.ensure_machine_key(machine)
                recipients = [self.get_machine_pubkey(machine)]

            case Shared():
                # Shared: encrypt to all machines that need this var
                machines = generator.machines
                for m in machines:
                    self.ensure_machine_key(m)
                recipients = [self.get_machine_pubkey(m) for m in machines]

            case PerExport(_):
                msg = "PerExport vars are not implemented yet"
                raise ClanError(msg)

        secret_file = self.secret_path(generator.key, var.name)
        secret_file.parent.mkdir(parents=True, exist_ok=True)

        self._run_age_encrypt(value, recipients, secret_file)

        # Write sidecar for shared secrets (not per-machine vars)
        if isinstance(generator.key.placement, Shared):
            return [secret_file, self._write_recipients(secret_file, recipients)]

        return [secret_file]

    def get(
        self,
        generator: GeneratorId,
        name: str,
    ) -> bytes:
        """Decrypt and return a secret.

        Uses two-step decryption: user identity → machine key → secret.
        """
        secret_file = self.secret_path(generator, name)

        if self._secret_cache is not None and secret_file in self._secret_cache:
            return self._secret_cache[secret_file]

        if not secret_file.exists():
            msg = f"Secret file not found: {secret_file}"
            raise ClanError(msg)

        # Determine which machine key to use
        machine_key: bytes | None = None
        match generator.placement:
            case PerMachine(machine=machine):
                machine_key = self.decrypt_machine_key(machine)
            case Shared():
                # For shared secrets, try each machine's key until one can
                # decrypt the secret. The secret may not be encrypted to all
                # machines yet (e.g. before fix() re-encrypts it).
                machines_dir = self.secrets_dir() / "age-keys" / "machines"
                if machines_dir.exists():
                    for machine_dir in machines_dir.iterdir():
                        if machine_dir.is_dir():
                            try:
                                candidate_key = self.decrypt_machine_key(
                                    machine_dir.name
                                )
                                value = self._run_age_decrypt_with_key(
                                    secret_file, candidate_key
                                )
                            except ClanError:
                                continue
                            else:
                                if self._secret_cache is not None:
                                    self._secret_cache[secret_file] = value
                                return value
            case PerExport(_):
                msg = "PerExport vars are not implemented yet"
                raise ClanError(msg)

        if machine_key is None:
            msg = f"Cannot decrypt secret {generator.name}/{name}: no accessible machine key found"
            raise ClanError(msg)

        value = self._run_age_decrypt_with_key(secret_file, machine_key)

        if self._secret_cache is not None:
            self._secret_cache[secret_file] = value

        return value

    def exists(self, generator: GeneratorId, name: str) -> bool:
        """Check if a secret exists."""
        return self.secret_path(generator, name).exists()

    def delete(self, generator: GeneratorId, name: str) -> Iterable[Path]:
        """Delete a secret."""
        secret_file = self.secret_path(generator, name)
        deleted_files: list[Path] = []
        if secret_file.exists():
            secret_file.unlink()
            deleted_files.append(secret_file)
            # Clean up empty parent directories
            parent = secret_file.parent
            while parent != self.secrets_dir() and parent.exists():
                if not any(parent.iterdir()):
                    parent.rmdir()
                    deleted_files.append(parent)
                    parent = parent.parent
                else:
                    break
        return deleted_files

    def delete_store(self, machine: str) -> Iterable[Path]:
        """Delete all secrets and machine key for a machine."""
        deleted_files: list[Path] = []

        # Delete secrets
        machine_dir = self.secrets_dir() / "clan-vars" / "per-machine" / machine
        if machine_dir.exists():
            deleted_files.extend(
                file for file in machine_dir.rglob("*") if file.is_file()
            )
            shutil.rmtree(machine_dir)
            deleted_files.append(machine_dir)

        # Delete machine key
        key_dir = self.machine_key_dir(machine)
        if key_dir.exists():
            deleted_files.extend(file for file in key_dir.rglob("*") if file.is_file())
            shutil.rmtree(key_dir)
            deleted_files.append(key_dir)

        return deleted_files

    # ── Upload / deployment ───────────────────────────────────────────────
    #
    # Encrypted .age files are included in the nix store as part of the
    # system closure (referenced directly from the flake directory).
    # Only the machine private key needs to be uploaded out-of-band,
    # since it must not be in the world-readable nix store.

    @override
    def populate_dir(
        self,
        generators: Sequence[GeneratorStore],
        machine: str,
        output_dir: Path,
        phases: list[str],
    ) -> None:
        """Prepare the machine private key and activation secrets for deployment.

        The decrypted machine private key is uploaded for on-target decryption
        of users/services secrets. Activation secrets are decrypted here and
        uploaded as plaintext (same approach as sops backend).
        """
        self.ensure_machine_key(machine)

        # Write decrypted machine private key
        machine_key = self.decrypt_machine_key(machine)
        key_file = output_dir / "key.txt"
        key_file.touch(mode=0o600)
        key_file.write_bytes(machine_key)

        # Decrypt and upload activation and partitioning secrets as plaintext.
        # Activation secrets go under activation/{gen}/{file}.
        # Partitioning secrets go directly under {gen}/{file} (no phase prefix),
        # matching the sops backend layout expected by the install code.
        plaintext_phases = []
        if "activation" in phases:
            plaintext_phases.append("activation")
        if "partitioning" in phases:
            plaintext_phases.append("partitioning")

        for phase in plaintext_phases:
            for generator in generators:
                for file in generator.files:
                    if file.needed_for == phase and file.secret:
                        secret_file = self.secret_path(generator.key, file.name)
                        if not secret_file.exists():
                            continue
                        plaintext = self._run_age_decrypt_with_key(
                            secret_file, machine_key
                        )
                        if phase == "activation":
                            target_path = (
                                output_dir / "activation" / generator.name / file.name
                            )
                        else:
                            target_path = output_dir / generator.name / file.name
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        target_path.touch(mode=0o600)
                        target_path.write_bytes(plaintext)
                        target_path.chmod(file.mode)

    @override
    def get_upload_directory(self, machine: str) -> str:
        """Get the target directory for machine key upload."""
        return self.flake.select(vars_age_secret_location(current_system(), [machine]))[
            machine
        ]["age"]["secretLocation"]

    @override
    def upload(
        self,
        generators: Sequence[GeneratorStore],
        machine: str,
        host: Host,
        phases: list[str],
    ) -> None:
        """Upload the machine private key to the target.

        Encrypted secrets are delivered via the nix store as part of the
        system closure. Only the machine key needs out-of-band upload.
        """
        with TemporaryDirectory(prefix="age-upload-") as _tempdir:
            upload_dir = Path(_tempdir).resolve()
            self.populate_dir(generators, machine, upload_dir, phases)
            upload(host, upload_dir, Path(self.get_upload_directory(machine)))

    # ── Health check and fix ──────────────────────────────────────────────

    @override
    def health_check(
        self,
        machine: str,
        generators: Sequence[GeneratorStore],
        file_name: str | None = None,
    ) -> str | None:
        """Check if secrets are properly configured for the age backend.

        Checks:
        - User recipients are configured
        - User identity is available
        - Machine key exists
        - For shared secrets: all machines' pubkeys are recipients
        """
        # Check if recipients are configured
        try:
            self.get_recipients(machine)
        except ClanError as e:
            return str(e)

        # Check if identity is available
        try:
            self.get_identity()
        except ClanError as e:
            return str(e)

        # Machine key is auto-created by ensure_machine_key() during generation,
        # so a missing key is not a health check failure — it just means
        # generation hasn't run yet.
        return None

    @override
    def fix(
        self,
        machine: str,
        generators: Sequence[GeneratorStore],
        file_name: str | None = None,
    ) -> None:
        """Fix secrets by re-encrypting machine keys and shared secrets as needed.

        - Re-encrypts machine private key to current user recipients
        - Re-encrypts shared secrets to all current machines' pubkeys
        - Per-machine secrets are never re-encrypted (machine key doesn't change)
        """
        # Re-key the machine key if user recipients changed
        if self.machine_pubkey_file(machine).exists():
            encrypted_key_file = self.machine_encrypted_key_file(machine)
            wanted = sorted(self.get_recipients(machine))
            current = self._read_recipients(encrypted_key_file)
            if current != wanted:
                self.rekey_machine_key(machine)
                commit_files(
                    [encrypted_key_file, self._recipients_file(encrypted_key_file)],
                    self.flake.path,
                    f"Re-encrypt machine key for '{machine}'",
                )

        # Re-encrypt shared secrets if machine recipients changed
        for generator in generators:
            if not isinstance(generator.key.placement, Shared):
                continue
            for file in generator.files:
                if file_name and file.name != file_name:
                    continue
                if not file.secret:
                    continue
                if not self.exists(generator.key, file.name):
                    continue

                secret_file = self.secret_path(generator.key, file.name)
                recipients = [self.get_machine_pubkey(m) for m in generator.machines]

                current = self._read_recipients(secret_file)
                if current == sorted(recipients):
                    continue

                # Decrypt with any available machine key, re-encrypt to all
                value = self.get(generator.key, file.name)
                self._run_age_encrypt(value, recipients, secret_file)
                self._write_recipients(secret_file, recipients)
                log.info(
                    f"Re-encrypted shared secret {generator.name}/{file.name} "
                    f"for {len(recipients)} machines"
                )
                commit_files(
                    [secret_file, self._recipients_file(secret_file)],
                    self.flake.path,
                    f"Re-encrypt shared secret {generator.name}/{file.name} for {len(recipients)} machines",
                )
