import logging

import pytest
from fastapi.testclient import TestClient

from clan_cli.webui.app import app


# TODO: Why stateful
@pytest.fixture(scope="session")
def api() -> TestClient:
    logging.getLogger("httpx").setLevel(level=logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    return TestClient(app)
