from pathlib import Path

from clan_cli.clan_uri import ClanParameters, ClanScheme, ClanURI


def test_get_internal() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com?flake_attr=myVM&password=1234")
    assert uri.get_internal() == "https://example.com?password=1234"

    uri = ClanURI("clan://~/Downloads")
    assert uri.get_internal().endswith("/Downloads")

    uri = ClanURI("clan:///home/user/Downloads")
    assert uri.get_internal() == "/home/user/Downloads"

    uri = ClanURI("clan://file:///home/user/Downloads")
    assert uri.get_internal() == "/home/user/Downloads"


def test_local_uri() -> None:
    # Create a ClanURI object from a local URI
    uri = ClanURI("clan://file:///home/user/Downloads")
    match uri.scheme:
        case ClanScheme.LOCAL.value(path):
            assert path == Path("/home/user/Downloads")  # type: ignore
        case _:
            assert False


def test_is_remote() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan://https://example.com")

    match uri.scheme:
        case ClanScheme.REMOTE.value(url):
            assert url == "https://example.com"  # type: ignore
        case _:
            assert False


def test_direct_local_path() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan://~/Downloads")
    assert uri.get_internal().endswith("/Downloads")


def test_direct_local_path2() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI("clan:///home/user/Downloads")
    assert uri.get_internal() == "/home/user/Downloads"


def test_remote_with_clanparams() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com")

    assert uri.params.flake_attr == "defaultVM"

    match uri.scheme:
        case ClanScheme.REMOTE.value(url):
            assert url == "https://example.com"  # type: ignore
        case _:
            assert False


def test_from_path_with_custom() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri_str = Path("/home/user/Downloads")
    params = ClanParameters(flake_attr="myVM")
    uri = ClanURI.from_path(uri_str, params)
    assert uri.params.flake_attr == "myVM"

    match uri.scheme:
        case ClanScheme.LOCAL.value(path):
            assert path == Path("/home/user/Downloads")  # type: ignore
        case _:
            assert False


def test_from_path_with_default() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri_str = Path("/home/user/Downloads")
    params = ClanParameters()
    uri = ClanURI.from_path(uri_str, params)
    assert uri.params.flake_attr == "defaultVM"

    match uri.scheme:
        case ClanScheme.LOCAL.value(path):
            assert path == Path("/home/user/Downloads")  # type: ignore
        case _:
            assert False


def test_from_str() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri_str = "https://example.com?password=asdasd&test=1234"
    params = ClanParameters(flake_attr="myVM")
    uri = ClanURI.from_str(url=uri_str, params=params)
    assert uri.params.flake_attr == "myVM"

    match uri.scheme:
        case ClanScheme.REMOTE.value(url):
            assert url == "https://example.com?password=asdasd&test=1234"  # type: ignore
        case _:
            assert False

    uri_str = "~/Downloads/democlan"
    params = ClanParameters(flake_attr="myVM")
    uri = ClanURI.from_str(url=uri_str, params=params)
    assert uri.params.flake_attr == "myVM"
    assert uri.get_internal().endswith("/Downloads/democlan")

    uri_str = "~/Downloads/democlan"
    uri = ClanURI.from_str(url=uri_str)
    assert uri.params.flake_attr == "defaultVM"
    assert uri.get_internal().endswith("/Downloads/democlan")

    uri_str = "clan://~/Downloads/democlan"
    uri = ClanURI.from_str(url=uri_str)
    assert uri.params.flake_attr == "defaultVM"
    assert uri.get_internal().endswith("/Downloads/democlan")


def test_remote_with_all_params() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI("clan://https://example.com?flake_attr=myVM&password=1234")
    assert uri.params.flake_attr == "myVM"

    match uri.scheme:
        case ClanScheme.REMOTE.value(url):
            assert url == "https://example.com?password=1234"  # type: ignore
        case _:
            assert False
