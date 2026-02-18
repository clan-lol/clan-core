"""Tests for install command target host resolution."""

from unittest.mock import patch

import pytest
from clan_lib.errors import ClanError

from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_install_resolves_target_from_inventory(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    """When no --target-host flag is given, use inventory deploy.targetHost."""
    flake.machines["myhost"] = create_test_machine_config()
    flake.inventory["machines"] = {
        "myhost": {"deploy": {"targetHost": "root@10.0.0.1"}},
    }
    flake.refresh()
    monkeypatch.chdir(flake.path)

    with patch("clan_cli.machines.install.run_machine_install") as mock_install:
        cli.run(
            [
                "machines",
                "install",
                "--flake",
                str(flake.path),
                "myhost",
                "--yes",
            ]
        )

    mock_install.assert_called_once()
    remote = mock_install.call_args.kwargs["target_host"]
    assert remote.address == "10.0.0.1"
    assert remote.user == "root"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_install_errors_without_target_host(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    """When no targetHost is configured anywhere, raise ClanError."""
    config = create_test_machine_config()
    config["clan"]["core"]["networking"]["targetHost"] = None
    flake.machines["myhost"] = config
    flake.refresh()
    monkeypatch.chdir(flake.path)

    with pytest.raises(ClanError, match="No target host for machine"):
        cli.run(
            [
                "machines",
                "install",
                "--flake",
                str(flake.path),
                "myhost",
                "--yes",
            ]
        )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_install_prefers_explicit_target_host_flag(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    """When --target-host is given, use it even if inventory has a targetHost."""
    flake.machines["myhost"] = create_test_machine_config()
    flake.inventory["machines"] = {
        "myhost": {"deploy": {"targetHost": "root@10.0.0.1"}},
    }
    flake.refresh()
    monkeypatch.chdir(flake.path)

    with patch("clan_cli.machines.install.run_machine_install") as mock_install:
        cli.run(
            [
                "machines",
                "install",
                "--flake",
                str(flake.path),
                "myhost",
                "--target-host",
                "root@192.168.1.1",
                "--yes",
            ]
        )

    mock_install.assert_called_once()
    remote = mock_install.call_args.kwargs["target_host"]
    assert remote.address == "192.168.1.1"
    assert remote.user == "root"
