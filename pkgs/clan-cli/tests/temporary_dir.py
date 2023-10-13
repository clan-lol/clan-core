import os
import tempfile
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def temporary_dir() -> Iterator[Path]:
    if os.getenv("TEST_KEEP_TEMPORARY_DIR"):
        temp_dir = tempfile.mkdtemp(prefix="pytest-")
        path = Path(temp_dir)
        yield path
        print("=========> Keeping temporary directory: ", path)
    else:
        with tempfile.TemporaryDirectory(prefix="pytest-") as dirpath:
            yield Path(dirpath)
