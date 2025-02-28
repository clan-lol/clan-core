import logging
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from sys import platform

import pytest

log = logging.getLogger(__name__)


TEMPDIR = None
# macOS' default temporary directory is too long for unix sockets
# This can break applications such as gpg-agent
if platform == "darwin":
    TEMPDIR = Path("/tmp")


@pytest.fixture
def temporary_home(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR")
    monkeypatch.setenv("HOME", str(temp_dir))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(temp_dir / ".config"))

    runtime_dir = temp_dir / "xdg-runtime-dir"
    runtime_dir.mkdir()
    runtime_dir.chmod(0o700)

    gpgdir = runtime_dir / "gpgagent"
    gpgdir.mkdir()
    gpgdir.chmod(0o700)
    monkeypatch.setenv("GPG_AGENT_INFO", str(gpgdir))

    # Iterate over all environment variables
    for key, value in os.environ.items():
        if xdg_runtime_dir and value.startswith(xdg_runtime_dir):
            monkeypatch.setenv(key, value.replace(xdg_runtime_dir, str(runtime_dir)))

    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.chdir(str(temp_dir))
    return temp_dir


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="pytest-", dir=TEMPDIR) as _dirpath:
        yield Path(_dirpath).resolve()
