import pytest

from clan_cli.custom_logger import setup_logging

# collect_ignore = ["./nixpkgs"]

pytest_plugins = [
    "clan_cli.tests.temporary_dir",
    "clan_cli.tests.root",
    "clan_cli.tests.age_keys",
    "clan_cli.tests.gpg_keys",
    "clan_cli.tests.git_repo",
    "clan_cli.tests.sshd",
    "clan_cli.tests.command",
    "clan_cli.tests.ports",
    "clan_cli.tests.hosts",
    "clan_cli.tests.runtime",
    "clan_cli.tests.fixtures_flakes",
    "clan_cli.tests.stdout",
    "clan_cli.tests.nix_config",
]


# Executed on pytest session start
def pytest_sessionstart(session: pytest.Session) -> None:
    # This function will be called once at the beginning of the test session
    print("Starting pytest session")
    # You can access the session config, items, testsfailed, etc.
    print(f"Session config: {session.config}")

    setup_logging(level="INFO")
