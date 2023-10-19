import logging
import os
import tempfile
from pathlib import Path
from typing import Iterator

import pytest

log = logging.getLogger(__name__)


@pytest.fixture
def temporary_home(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    if os.getenv("TEST_KEEP_TEMPORARY_DIR") is not None:
        temp_dir = tempfile.mkdtemp(prefix="pytest-")
        path = Path(temp_dir)
        log.debug("Temp HOME directory: %s", str(path))
        monkeypatch.setenv("HOME", str(temp_dir))
        yield path
    else:
        log.debug("TEST_KEEP_TEMPORARY_DIR not set, using TemporaryDirectory")
        with tempfile.TemporaryDirectory(prefix="pytest-") as dirpath:
            monkeypatch.setenv("HOME", str(dirpath))
            log.debug("Temp HOME directory: %s", str(dirpath))
            yield Path(dirpath)
