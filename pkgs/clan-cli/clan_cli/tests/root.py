import os
from pathlib import Path

import pytest

TEST_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TEST_ROOT.parent
if CLAN_CORE_ := os.environ.get("CLAN_CORE_PATH"):
    CLAN_CORE = Path(CLAN_CORE_)
else:
    CLAN_CORE = PROJECT_ROOT.parent.parent.parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    Root directory the clan-cli
    """
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_root() -> Path:
    """
    Root directory of the tests
    """
    return TEST_ROOT


@pytest.fixture(scope="session")
def test_lib_root() -> Path:
    """
    Root directory of the clan-lib tests
    """
    return PROJECT_ROOT.parent / "clan_lib" / "tests"


@pytest.fixture(scope="session")
def clan_core() -> Path:
    """
    Directory of the clan-core flake
    """
    return CLAN_CORE
