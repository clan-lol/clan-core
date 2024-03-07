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

    assert uri.machine.name == "defaultVM"

    match uri.url:
        case ClanUrl.REMOTE.value(url):
            assert url == "https://example.com"  # type: ignore
        case _:
            assert False


def test_remote_with_all_params() -> None:
    uri = ClanURI("clan://https://example.com?password=12345#myVM#secondVM?dummy_opt=1")
    assert uri.machine.name == "myVM"
    assert uri._machines[1].name == "secondVM"
    assert uri._machines[1].params.dummy_opt == "1"
    match uri.url:
        case ClanUrl.REMOTE.value(url):
            assert url == "https://example.com?password=12345"  # type: ignore
        case _:
            assert False


def test_from_str_remote() -> None:
    uri = ClanURI.from_str(url="https://example.com", machine_name="myVM")
    assert uri.get_url() == "https://example.com"
    assert uri.get_orig_uri() == "clan://https://example.com#myVM"
    assert uri.machine.name == "myVM"
    assert len(uri._machines) == 1
    match uri.url:
        case ClanUrl.REMOTE.value(url):
            assert url == "https://example.com"  # type: ignore
        case _:
            assert False


def test_from_str_local() -> None:
    uri = ClanURI.from_str(url="~/Projects/democlan", machine_name="myVM")
    assert uri.get_url().endswith("/Projects/democlan")
    assert uri.get_orig_uri() == "clan://~/Projects/democlan#myVM"
    assert uri.machine.name == "myVM"
    assert len(uri._machines) == 1
    match uri.url:
        case ClanUrl.LOCAL.value(path):
            assert str(path).endswith("/Projects/democlan")  # type: ignore
        case _:
            assert False


def test_from_str_local_no_machine() -> None:
    uri = ClanURI.from_str("~/Projects/democlan")
    assert uri.get_url().endswith("/Projects/democlan")
    assert uri.get_orig_uri() == "clan://~/Projects/democlan"
    assert uri.machine.name == "defaultVM"
    assert len(uri._machines) == 1
    match uri.url:
        case ClanUrl.LOCAL.value(path):
            assert str(path).endswith("/Projects/democlan")  # type: ignore
        case _:
            assert False


def test_from_str_local_no_machine2() -> None:
    uri = ClanURI.from_str("~/Projects/democlan#syncthing-peer1")
    assert uri.get_url().endswith("/Projects/democlan")
    assert uri.get_orig_uri() == "clan://~/Projects/democlan#syncthing-peer1"
    assert uri.machine.name == "syncthing-peer1"
    assert len(uri._machines) == 1
    match uri.url:
        case ClanUrl.LOCAL.value(path):
            assert str(path).endswith("/Projects/democlan")  # type: ignore
        case _:
            assert False
