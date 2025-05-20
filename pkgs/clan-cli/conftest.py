import logging

import pytest
from clan_lib.custom_logger import setup_logging

# Every fixture registered here will be available in clan_cli and clan_lib
pytest_plugins = [
    "clan_cli.tests.temporary_dir",
    "clan_cli.tests.root",
    "clan_cli.tests.sshd",
    "clan_cli.tests.hosts",
    "clan_cli.tests.command",
    "clan_cli.tests.ports",
]


# Executed on pytest session start
def pytest_sessionstart(session: pytest.Session) -> None:
    # This function will be called once at the beginning of the test session
    print("Starting pytest session")
    # You can access the session config, items, testsfailed, etc.
    print(f"Session config: {session.config}")

    setup_logging(logging.DEBUG)
