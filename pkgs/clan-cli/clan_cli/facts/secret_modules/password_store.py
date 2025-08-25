import os
import subprocess
from pathlib import Path
from typing import override

from clan_lib.cmd import Log, RunOpts
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_shell
from clan_lib.ssh.host import Host

from clan_cli.facts.secret_modules import SecretStoreBase


class SecretStore(SecretStoreBase):
    def __init__(self, machine: Machine) -> None:
        self.machine = machine

    def set(
        self,
        service: str,
        name: str,
        value: bytes,
        groups: list[str],
    ) -> Path | None:
        del service, groups  # Unused but kept for API compatibility
        subprocess.run(
            nix_shell(
                ["pass"],
                ["pass", "insert", "-m", f"machines/{self.machine.name}/{name}"],
            ),
            input=value,
            check=True,
        )
        return None  # we manage the files outside of the git repo

    def get(self, service: str, name: str) -> bytes:
        del service  # Unused but kept for API compatibility
        return subprocess.run(
            nix_shell(
                ["pass"],
                ["pass", "show", f"machines/{self.machine.name}/{name}"],
            ),
            check=True,
            stdout=subprocess.PIPE,
        ).stdout

    def exists(self, service: str, name: str) -> bool:
        del service  # Unused but kept for API compatibility
        password_store = os.environ.get(
            "PASSWORD_STORE_DIR",
            f"{os.environ['HOME']}/.password-store",
        )
        secret_path = Path(password_store) / f"machines/{self.machine.name}/{name}.gpg"
        return secret_path.exists()

    def generate_hash(self) -> bytes:
        password_store = os.environ.get(
            "PASSWORD_STORE_DIR",
            f"{os.environ['HOME']}/.password-store",
        )
        hashes = []
        hashes.append(
            subprocess.run(
                nix_shell(
                    ["git"],
                    [
                        "git",
                        "-C",
                        password_store,
                        "log",
                        "-1",
                        "--format=%H",
                        f"machines/{self.machine.name}",
                    ],
                ),
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.strip(),
        )
        for symlink in Path(password_store).glob(f"machines/{self.machine.name}/**/*"):
            if symlink.is_symlink():
                hashes.append(
                    subprocess.run(
                        nix_shell(
                            ["git"],
                            [
                                "git",
                                "-C",
                                password_store,
                                "log",
                                "-1",
                                "--format=%H",
                                str(symlink),
                            ],
                        ),
                        stdout=subprocess.PIPE,
                        check=False,
                    ).stdout.strip(),
                )

        # we sort the hashes to make sure that the order is always the same
        hashes.sort()
        return b"\n".join(hashes)

    @override
    def needs_upload(self, host: Host) -> bool:
        local_hash = self.generate_hash()
        with host.host_connection() as ssh:
            remote_hash = ssh.run(
                # TODO get the path to the secrets from the machine
                ["cat", f"{self.machine.secrets_upload_directory}/.pass_info"],
                RunOpts(log=Log.STDERR, check=False),
            ).stdout.strip()

        if not remote_hash:
            print("remote hash is empty")
            return True

        return local_hash.decode() != remote_hash

    def upload(self, output_dir: Path) -> None:
        os.umask(0o077)
        for service in self.machine.facts_data:
            for secret in self.machine.facts_data[service]["secret"]:
                if isinstance(secret, dict):
                    secret_name = secret["name"]
                else:
                    # TODO: drop old format soon
                    secret_name = secret
                (output_dir / secret_name).write_bytes(self.get(service, secret_name))
        (output_dir / ".pass_info").write_bytes(self.generate_hash())
