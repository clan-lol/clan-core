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
        monkeypatch.chdir(str(path))
        yield path
    else:
        with tempfile.TemporaryDirectory(prefix="pytest-") as dirpath:
            monkeypatch.setenv("HOME", str(dirpath))
            monkeypatch.setenv("XDG_CONFIG_HOME", str(Path(dirpath) / ".config"))
            monkeypatch.chdir(str(dirpath))
            log.debug("Temp HOME directory: %s", str(dirpath))
            yield Path(dirpath)
