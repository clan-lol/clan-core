import pytest
from clan_lib.async_run import AsyncRuntime


@pytest.fixture
def runtime() -> AsyncRuntime:
    return AsyncRuntime()
