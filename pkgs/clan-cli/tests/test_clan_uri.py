from pathlib import Path

from clan_cli.clan_uri import ClanURI, ClanUrl


def test_get_url() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com?password=1234#myVM")
    assert uri.get_url() == "https://example.com?password=1234"

    uri = ClanURI("clan://~/Downloads")
    assert uri.get_url().endswith("/Downloads")

    uri = ClanURI("clan:///home/user/Downloads")
    assert uri.get_url() == "/home/user/Downloads"

    uri = ClanURI("clan://file:///home/user/Downloads")
    assert uri.get_url() == "/home/user/Downloads"


def test_local_uri() -> None:
    # Create a ClanURI object from a local URI
    uri = ClanURI("clan://file:///home/user/Downloads")
    match uri.url:
        case ClanUrl.LOCAL.value(path):
            assert path == Path("/home/user/Downloads")  # type: ignore
        case _:
            assert False


def test_is_remote() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan://https://example.com")

    match uri.url:
        case ClanUrl.REMOTE.value(url):
            assert url == "https://example.com"  # type: ignore
        case _:
            assert False


def test_direct_local_path() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan://~/Downloads")
    assert uri.get_url().endswith("/Downloads")


def test_direct_local_path2() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan:///home/user/Downloads")
    assert uri.get_url() == "/home/user/Downloads"


def test_remote_with_clanparams() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com")

    assert uri.machines[0].name == "defaultVM"

    match uri.url:
        case ClanUrl.REMOTE.value(url):
            assert url == "https://example.com"  # type: ignore
        case _:
            assert False


def test_remote_with_all_params() -> None:
    uri = ClanURI("clan://https://example.com?password=12345#myVM#secondVM")
    assert uri.machines[0].name == "myVM"
    assert uri.machines[1].name == "secondVM"
    match uri.url:
        case ClanUrl.REMOTE.value(url):
            assert url == "https://example.com?password=12345"  # type: ignore
        case _:
            assert False
