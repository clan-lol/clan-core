import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class GpgKey:
    fingerprint: str
    gpg_home: Path


@pytest.fixture
def gpg_key(
    temp_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_root: Path,
) -> GpgKey:
    gpg_home = temp_dir / "gnupghome"

    shutil.copytree(test_root / "data" / "gnupg-home", gpg_home)
    monkeypatch.setenv("GNUPGHOME", str(gpg_home))

    return GpgKey("9A9B2741C8062D3D3DF1302D8B049E262A5CA255", gpg_home)
