import tempfile
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def temporary_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="pytest-") as dirpath:
        yield Path(dirpath)
