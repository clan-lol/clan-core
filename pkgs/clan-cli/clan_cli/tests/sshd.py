import os
import shutil
import string
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from sys import platform
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .command import Command
    from .ports import PortFunction


class SshdError(Exception):
    pass


class Sshd:
    def __init__(self, port: int, proc: subprocess.Popen[str], key: str) -> None:
        self.port = port
        self.proc = proc
        self.key = key


class SshdConfig:
    def __init__(
        self,
        path: Path,
        login_shell: Path,
        key: str,
        preload_lib: Path,
        log_file: Path,
    ) -> None:
        self.path = path
        self.login_shell = login_shell
        self.key = key
        self.preload_lib = preload_lib
        self.log_file = log_file


@pytest.fixture(scope="session")
def sshd_config(test_root: Path) -> Iterator[SshdConfig]:
    # FIXME, if any parent of the sshd directory is world-writable then sshd will refuse it.
    # we use .direnv instead since it's already in .gitignore
    with TemporaryDirectory(prefix="sshd-", ignore_cleanup_errors=True) as _dir:
        tmpdir = Path(_dir)
        host_key = test_root / "data" / "ssh_host_ed25519_key"
        host_key.chmod(0o600)
        template = (test_root / "data" / "sshd_config").read_text()
        sshd = shutil.which("sshd")
        assert sshd is not None
        sshdp = Path(sshd)
        sftp_server = sshdp.parent.parent / "libexec" / "sftp-server"
        assert sftp_server is not None
        content = string.Template(template).substitute(
            {"host_key": host_key, "sftp_server": sftp_server},
        )
        config = tmpdir / "sshd_config"
        config.write_text(content)
        bin_path = tmpdir / "bin"
        login_shell = bin_path / "shell"
        fake_sudo = bin_path / "sudo"
        login_shell.parent.mkdir(parents=True)

        bash = shutil.which("bash")
        path = os.environ["PATH"]
        assert bash is not None

        login_shell.write_text(
            f"""#!{bash}
set -x
if [[ -f /etc/profile ]]; then
  source /etc/profile
fi
export PATH="{bin_path}:{path}"
exec {bash} -l "${{@}}"
        """,
        )
        login_shell.chmod(0o755)

        fake_sudo.write_text(
            f"""#!{bash}
shift
exec "${{@}}"
        """,
        )
        fake_sudo.chmod(0o755)

        lib_path = None

        extension = ".so"
        if platform == "darwin":
            extension = ".dylib"
        link_lib_flag = "-shared"
        if platform == "darwin":
            link_lib_flag = "-dynamiclib"

        # This enforces a login shell by overriding the login shell of `getpwnam(3)`
        lib_path = tmpdir / f"libgetpwnam-preload.${extension}"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                link_lib_flag,
                "-o",
                lib_path,
                str(test_root / "getpwnam-preload.c"),
            ],
            check=True,
        )
        log_file = tmpdir / "sshd.log"
        yield SshdConfig(config, login_shell, str(host_key), lib_path, log_file)


@pytest.fixture
def sshd(
    sshd_config: SshdConfig,
    command: "Command",
    unused_tcp_port: "PortFunction",
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Sshd]:
    port = unused_tcp_port()
    sshd = shutil.which("sshd")
    assert sshd is not None, "no sshd binary found"
    env = {}
    preload_env_name = "LD_PRELOAD"
    if platform == "darwin":
        preload_env_name = "DYLD_INSERT_LIBRARIES"

    env = {
        preload_env_name: str(sshd_config.preload_lib),
        "LOGIN_SHELL": str(sshd_config.login_shell),
    }
    proc = command.run(
        [
            sshd,
            "-E",
            str(sshd_config.log_file),
            "-f",
            str(sshd_config.path),
            "-D",
            "-p",
            str(port),
        ],
        extra_env=env,
    )
    monkeypatch.delenv("SSH_AUTH_SOCK", raising=False)

    timeout = 5
    start_time = time.time()

    while True:
        print(sshd_config.path)
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
                ],
                check=False,
            ).returncode
            == 0
        ):
            yield Sshd(port, proc, sshd_config.key)
            return
        else:
            rc = proc.poll()
            if rc is not None:
                msg = f"sshd processes was terminated with {rc}"
                raise SshdError(msg)
            if time.time() - start_time > timeout:
                msg = "Timeout while waiting for sshd to be ready"
                raise SshdError(msg)
            time.sleep(0.1)
