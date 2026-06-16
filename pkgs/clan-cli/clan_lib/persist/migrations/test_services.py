import json
import subprocess
from pathlib import Path

import pytest

from clan_lib.errors import ClanError
from clan_lib.persist.migrations import run_inventory_migrations

from .services import migrate_services


def test_empty_services_removed() -> None:
    inventory: dict = {"instances": {}, "services": {}}
    assert migrate_services(inventory) is True
    assert "services" not in inventory
    assert "instances" in inventory


def test_no_services_key_is_noop() -> None:
    inventory: dict = {"instances": {"foo": {}}}
    assert migrate_services(inventory) is False
    assert inventory == {"instances": {"foo": {}}}


def test_non_empty_services_raises() -> None:
    inventory: dict = {
        "services": {"borgbackup": {"prod": {"roles": {"server": {}}}}},
    }
    with pytest.raises(ClanError, match=r"non-empty.*services"):
        migrate_services(inventory)
    # Dict untouched on error
    assert "services" in inventory


def test_idempotent_after_removal() -> None:
    inventory: dict = {"instances": {}}
    assert migrate_services(inventory) is False
    assert migrate_services(inventory) is False


def test_run_inventory_migrations_writes_file(tmp_path: Path) -> None:
    """End-to-end: stale empty services key is stripped from the JSON file."""
    inventory_file = tmp_path / "inventory.json"
    inventory_file.write_text(json.dumps({"instances": {}, "services": {}}))

    # init a git repo so commit_file doesn't fail
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "add", "inventory.json"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    run_inventory_migrations(tmp_path)

    result = json.loads(inventory_file.read_text())
    assert "services" not in result
    assert "instances" in result


def test_run_inventory_migrations_noop_no_file(tmp_path: Path) -> None:
    """No inventory.json at all — should be a silent no-op."""
    run_inventory_migrations(tmp_path)  # must not raise


def test_run_inventory_migrations_noop_clean(tmp_path: Path) -> None:
    """inventory.json without services key — no write, no commit."""
    inventory_file = tmp_path / "inventory.json"
    original = json.dumps({"instances": {}})
    inventory_file.write_text(original)

    run_inventory_migrations(tmp_path)

    # File unchanged
    assert inventory_file.read_text() == original
