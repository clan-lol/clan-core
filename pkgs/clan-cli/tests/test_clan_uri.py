import pytest

from clan_cli.clan_uri import ClanURI
from clan_cli.errors import ClanError


def test_local_uri() -> None:
    # Create a ClanURI object from a local URI
    uri = ClanURI("clan://file:///home/user/Downloads")
    # Check that the URI is local
    assert uri.is_local()
    # Check that the URI is not remote
    assert not uri.is_remote()
    # Check that the URI path is correct
    assert uri.path == "/home/user/Downloads"


def test_unsupported_schema() -> None:
    with pytest.raises(ClanError, match="Unsupported scheme: ftp"):
        # Create a ClanURI object from an unsupported URI
        ClanURI("clan://ftp://ftp.example.com")


def test_is_remote() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan://https://example.com")
    # Check that the URI is remote
    assert uri.is_remote()
    # Check that the URI is not local
    assert not uri.is_local()
    # Check that the URI path is correct
    assert uri.path == ""

    assert uri.url == "https://example.com"
