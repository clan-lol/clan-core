from pathlib import Path

import pytest
from clan_cli.clan_uri import ClanURI
from clan_cli.flake import Flake
from fixtures_flakes import ClanFlake


def test_get_url() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI.from_str("clan://https://example.com?password=1234#myVM")
    assert uri.get_url() == "https://example.com?password=1234"

    uri = ClanURI.from_str("clan://~/Downloads")
    assert uri.get_url().endswith("/Downloads")

    uri = ClanURI.from_str("clan:///home/user/Downloads")
    assert uri.get_url() == "/home/user/Downloads"

    uri = ClanURI.from_str("clan://file:///home/user/Downloads")
    assert uri.get_url() == "file:///home/user/Downloads"


@pytest.mark.impure
def test_is_local(flake: ClanFlake) -> None:
    uri = ClanURI.from_str(f"clan://git+file://{flake.path}")
    assert uri.get_url() == str(flake.path)
    assert uri.flake.is_local
    myflake = Flake(f"git+file://{flake.path}")
    assert myflake.is_local


def test_firefox_strip_uri() -> None:
    uri = ClanURI.from_str("clan://git+https//git.clan.lol/clan/democlan.git")
    assert uri.get_url() == "git+https://git.clan.lol/clan/democlan.git"


def test_local_uri(temp_dir: Path) -> None:
    flake_nix = temp_dir / "flake.nix"
    flake_nix.write_text("outputs = _: {}")

    # Create a ClanURI object from a local URI
    uri = ClanURI.from_str(f"clan://file://{temp_dir}")
    assert uri.flake.path == temp_dir


def test_is_remote() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI.from_str("clan://https://example.com")
    assert uri.flake.identifier == "https://example.com"


def test_direct_local_path() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI.from_str("clan://~/Downloads")
    assert uri.get_url().endswith("/Downloads")


def test_direct_local_path2() -> None:
    # Create a ClanURI object from a remote URI
    uri = ClanURI.from_str("clan:///home/user/Downloads")
    assert uri.get_url() == "/home/user/Downloads"


def test_remote_with_clanparams() -> None:
    # Create a ClanURI object from a remote URI with parameters
    uri = ClanURI.from_str("clan://https://example.com")

    assert uri.machine_name == "defaultVM"
    assert uri.flake.identifier == "https://example.com"


def test_from_str_remote() -> None:
    uri = ClanURI.from_str(url="https://example.com", machine_name="myVM")
    assert uri.get_url() == "https://example.com"
    assert uri.machine_name == "myVM"
    assert uri.flake.identifier == "https://example.com"


def test_from_str_local(temp_dir: Path) -> None:
    flake_nix = temp_dir / "flake.nix"
    flake_nix.write_text("outputs = _: {}")

    uri = ClanURI.from_str(url=str(temp_dir), machine_name="myVM")
    assert uri.get_url().endswith(str(temp_dir))
    assert uri.machine_name == "myVM"
    assert uri.flake.is_local
    assert str(uri.flake).endswith(str(temp_dir))


def test_from_str_local_no_machine(temp_dir: Path) -> None:
    flake_nix = temp_dir / "flake.nix"
    flake_nix.write_text("outputs = _: {}")

    uri = ClanURI.from_str(str(temp_dir))
    assert uri.get_url().endswith(str(temp_dir))
    assert uri.machine_name == "defaultVM"
    assert uri.flake.is_local
    assert str(uri.flake).endswith(str(temp_dir))
