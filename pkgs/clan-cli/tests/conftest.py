import pytest
from clan_cli.custom_logger import setup_logging

pytest_plugins = [
    "temporary_dir",
    "root",
    "age_keys",
    "gpg_keys",
    "git_repo",
    "sshd",
    "command",
    "ports",
    "hosts",
    "runtime",
    "fixtures_flakes",
    "stdout",
    "nix_config",
]


# Executed on pytest session start
def pytest_sessionstart(session: pytest.Session) -> None:
    # This function will be called once at the beginning of the test session
    print("Starting pytest session")
    # You can access the session config, items, testsfailed, etc.
    print(f"Session config: {session.config}")

    setup_logging(level="DEBUG")
