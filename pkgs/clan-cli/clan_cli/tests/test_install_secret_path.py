"""Regression tests for install secret upload path (issue #6049)."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_lib.flake import Flake
from clan_lib.machines.install import InstallOptions, run_machine_install
from clan_lib.machines.machines import Machine
from clan_lib.ssh.remote import Remote


def _find_extra_files_arg(cmd: list[Any]) -> Path | None:
    """Extract --extra-files directory path from nixos-anywhere command."""
    for i, arg in enumerate(cmd):
        if arg == "--extra-files" and i + 1 < len(cmd):
            return Path(cmd[i + 1])
    return None


@pytest.mark.with_core
@pytest.mark.parametrize(
    ("secret_upload_dir", "expected_relative_path"),
    [
        pytest.param(None, "var/lib/sops-nix", id="default"),
        pytest.param("/custom/sops-secrets", "custom/sops-secrets", id="custom"),
    ],
)
def test_sops_install_secret_path(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    secret_upload_dir: str | None,
    expected_relative_path: str,
) -> None:
    """Verify secrets are placed at configured secretUploadDirectory for nixos-anywhere."""
    config = flake_with_sops.machines["test_machine"] = create_test_machine_config()
    if secret_upload_dir is not None:
        config["clan"]["core"]["vars"]["sops"]["secretUploadDirectory"] = (
            secret_upload_dir
        )
    generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    generator["files"]["my_secret"]["secret"] = True
    generator["script"] = 'echo -n "test_secret_value" > "$out"/my_secret'

    flake_with_sops.refresh()
    monkeypatch.chdir(flake_with_sops.path)
    cli.run(["vars", "generate", "--flake", str(flake_with_sops.path), "test_machine"])

    machine = Machine(name="test_machine", flake=Flake(str(flake_with_sops.path)))

    verification_result: str | None = None

    def mock_run(cmd: list[Any], *_args: object, **_kwargs: object) -> MagicMock:
        nonlocal verification_result
        extra_files_dir = _find_extra_files_arg(cmd)
        if extra_files_dir is not None:
            key_path = extra_files_dir / expected_relative_path / "key.txt"
            if not key_path.exists():
                verification_result = (
                    f"Expected {key_path}, found: {list(extra_files_dir.rglob('*'))}"
                )
            elif not key_path.read_text().startswith("AGE-SECRET-KEY-"):
                verification_result = f"Invalid age key: {key_path.read_text()[:50]}..."
            else:
                verification_result = "ok"
        result = MagicMock()
        result.returncode = 0
        return result

    with patch("clan_lib.machines.install.run", side_effect=mock_run):
        run_machine_install(
            InstallOptions(machine=machine),
            Remote(address="root@test.example.com"),
        )

    assert verification_result == "ok", verification_result or "--extra-files not found"


@pytest.mark.with_core
@pytest.mark.parametrize(
    ("secret_location", "expected_path"),
    [
        pytest.param(None, "/etc/secret-vars", id="default"),
        pytest.param("/etc/pass-secrets", "/etc/pass-secrets", id="custom"),
    ],
)
def test_password_store_upload_directory(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    secret_location: str | None,
    expected_path: str,
) -> None:
    """Verify get_upload_directory returns configured secretLocation."""
    config = flake.machines["test_machine"] = create_test_machine_config()
    config["clan"]["core"]["vars"]["settings"]["secretStore"] = "password-store"
    if secret_location is not None:
        config["clan"]["core"]["vars"]["password-store"]["secretLocation"] = (
            secret_location
        )

    flake.refresh()
    monkeypatch.chdir(flake.path)

    machine = Machine(name="test_machine", flake=Flake(str(flake.path)))
    assert machine.secret_vars_store.get_upload_directory(machine.name) == expected_path
