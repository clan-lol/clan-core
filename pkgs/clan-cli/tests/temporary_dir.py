import logging
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

log = logging.getLogger(__name__)


@pytest.fixture
def temporary_home(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    env_dir = os.getenv("TEST_TEMPORARY_DIR")
    if env_dir is not None:
        path = Path(env_dir).resolve()
        log.debug("Temp HOME directory: %s", str(path))
        monkeypatch.setenv("HOME", str(path))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(path / ".config"))
        runtime_dir = path / "xdg-runtime-dir"
        runtime_dir.mkdir()
        runtime_dir.chmod(0o700)
        monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime_dir))
        monkeypatch.chdir(str(path))
        yield path
    else:
        with tempfile.TemporaryDirectory(prefix="pytest-") as dirpath:
            monkeypatch.setenv("HOME", str(dirpath))
            monkeypatch.setenv("XDG_CONFIG_HOME", str(Path(dirpath) / ".config"))
            runtime_dir = Path(dirpath) / "xdg-runtime-dir"
            runtime_dir.mkdir()
            runtime_dir.chmod(0o700)
            monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime_dir))
            monkeypatch.chdir(str(dirpath))
            log.debug("Temp HOME directory: %s", str(dirpath))
            yield Path(dirpath)
