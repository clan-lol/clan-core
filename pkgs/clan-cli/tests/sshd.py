import os
import shutil
import subprocess
import time
from pathlib import Path
from sys import platform
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Iterator

import pytest

if TYPE_CHECKING:
    from command import Command
    from ports import Ports


class Sshd:
    def __init__(self, port: int, proc: subprocess.Popen[str], key: str) -> None:
        self.port = port
        self.proc = proc
        self.key = key


class SshdConfig:
    def __init__(
        self, path: Path, login_shell: Path, key: str, preload_lib: Path
    ) -> None:
        self.path = path
        self.login_shell = login_shell
        self.key = key
        self.preload_lib = preload_lib


@pytest.fixture(scope="session")
def sshd_config(project_root: Path, test_root: Path) -> Iterator[SshdConfig]:
    # FIXME, if any parent of `project_root` is world-writable than sshd will refuse it.
    with TemporaryDirectory(dir=project_root) as _dir:
        dir = Path(_dir)
        host_key = dir / "host_ssh_host_ed25519_key"
        subprocess.run(
            [
                "ssh-keygen",
                "-t",
                "ed25519",
                "-f",
                host_key,
                "-N",
                "",
            ],
            check=True,
        )

        sshd_config = dir / "sshd_config"
        sshd_config.write_text(
            f"""
        HostKey {host_key}
        LogLevel DEBUG3
        # In the nix build sandbox we don't get any meaningful PATH after login
        MaxStartups 64:30:256
        AuthorizedKeysFile {host_key}.pub
        AcceptEnv REALPATH
        """
        )
        login_shell = dir / "shell"

        bash = shutil.which("bash")
        path = os.environ["PATH"]
        assert bash is not None

        login_shell.write_text(
            f"""#!{bash}
if [[ -f /etc/profile ]]; then
  source /etc/profile
fi
if [[ -n "$REALPATH" ]]; then
   export PATH="$REALPATH:${path}"
else
   export PATH="${path}"
fi
exec {bash} -l "${{@}}"
        """
        )
        login_shell.chmod(0o755)

        lib_path = None
        assert (
            platform == "linux"
        ), "we do not support the ld_preload trick on non-linux just now"

        # This enforces a login shell by overriding the login shell of `getpwnam(3)`
        lib_path = dir / "libgetpwnam-preload.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-o",
                lib_path,
                str(test_root / "getpwnam-preload.c"),
            ],
            check=True,
        )

        yield SshdConfig(sshd_config, login_shell, str(host_key), lib_path)


@pytest.fixture
def sshd(sshd_config: SshdConfig, command: "Command", ports: "Ports") -> Iterator[Sshd]:
    port = ports.allocate(1)
    sshd = shutil.which("sshd")
    assert sshd is not None, "no sshd binary found"
    env = {}
    env = dict(
        LD_PRELOAD=str(sshd_config.preload_lib),
        LOGIN_SHELL=str(sshd_config.login_shell),
    )
    proc = command.run(
        [sshd, "-f", str(sshd_config.path), "-D", "-p", str(port)], extra_env=env
    )

    while True:
        if (
            subprocess.run(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-i",
                    sshd_config.key,
                    "localhost",
                    "-p",
                    str(port),
                    "true",
                ]
            ).returncode
            == 0
        ):
            yield Sshd(port, proc, sshd_config.key)
            return
        else:
            rc = proc.poll()
            if rc is not None:
                raise Exception(f"sshd processes was terminated with {rc}")
            time.sleep(0.1)
