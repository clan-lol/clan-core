import pytest

from clan_cli.clan_uri import ClanURI, ClanScheme
from clan_cli.errors import ClanError
from pathlib import Path

def test_local_uri() -> None:
    # Create a ClanURI object from a local URI
    uri = ClanURI("clan://file:///home/user/Downloads")
    match uri.scheme:
        case ClanScheme.FILE.value(path):
            assert path == Path("/home/user/Downloads") # type: ignore
        case _:
            assert False

def test_unsupported_schema() -> None:
    with pytest.raises(ClanError, match="Unsupported scheme: ftp"):
        # Create a ClanURI object from an unsupported URI
        ClanURI("clan://ftp://ftp.example.com")


def test_is_remote() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan://https://example.com")

    match uri.scheme:
        case ClanScheme.HTTPS.value(url):
            assert url ==  "https://example.com" # type: ignore
        case _:
            assert False

def remote_with_clanparams() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com?flake_attr=defaultVM")

    assert uri.params.flake_attr == "defaultVM"

    match uri.scheme:
        case ClanScheme.HTTPS.value(url):
            assert url ==  "https://example.com" # type: ignore
        case _:
            assert False

def remote_with_all_params() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com?flake_attr=defaultVM&machine=vm1&password=1234")

    assert uri.params.flake_attr == "defaultVM"
    assert uri.params.machine == "vm1"

    match uri.scheme:
        case ClanScheme.HTTPS.value(url):
            assert url ==  "https://example.com&password=1234" # type: ignore
        case _:
            assert False