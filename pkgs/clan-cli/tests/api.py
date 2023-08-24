import pytest
from fastapi.testclient import TestClient

from clan_cli.webui.app import app


@pytest.fixture(scope="session")
def api() -> TestClient:
    return TestClient(app)
