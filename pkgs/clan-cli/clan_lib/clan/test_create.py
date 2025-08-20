from pathlib import Path
from typing import Any

import pytest

from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore


@pytest.mark.with_core
def test_create_simple(tmp_path: Path, offline_flake_hook: Any) -> None:
    """Template = 'default'
    # All default params
    """
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template="default",
        _postprocess_flake_hook=offline_flake_hook,
    )

    create_clan(opts)

    assert dest.exists()
    assert dest.is_dir()

    flake = Flake(str(dest))

    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    # Smoke check that some inventory data is present
    assert isinstance(inventory, dict)
    assert "meta" in inventory
    assert "machines" in inventory
    assert "instances" in inventory


@pytest.mark.with_core
def test_can_handle_path_without_slash(
    tmp_path: Path,
    offline_flake_hook: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tests for a regression, where it broke when the path is a single word like `foo`.
    The flake identifier was interpreted as an external flake.
    """
    monkeypatch.chdir(tmp_path)
    dest = Path("test_clan")

    opts = CreateOptions(
        dest=dest,
        template="default",
        _postprocess_flake_hook=offline_flake_hook,
    )

    create_clan(opts)

    assert dest.exists()
    assert dest.is_dir()


@pytest.mark.with_core
def test_create_with_name(tmp_path: Path, offline_flake_hook: Any) -> None:
    """Template = 'default'
    # All default params
    """
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template="minimal",  # important the default template is not writable
        initial={
            "name": "test-clan",  # invalid hostname
            "description": "Test description",
            # Note: missing "icon", should be okay and should not get persisted
        },
        _postprocess_flake_hook=offline_flake_hook,
    )
    create_clan(opts)

    assert dest.exists()
    assert dest.is_dir()

    flake = Flake(str(dest))

    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    # Smoke check that some inventory data is present
    assert isinstance(inventory, dict)
    assert "meta" in inventory
    assert "machines" in inventory
    assert "instances" in inventory

    meta = inventory.get("meta", {})
    assert meta.get("name") == "test-clan"
    assert meta.get("description") == "Test description"
    assert meta.get("icon") is None, "Icon should not be set if not provided"


# When using the 'default' template, the name is set in nix
# Which means we cannot set it via initial data
# This test ensures that we cannot set nix values
# We might want to change this in the future
@pytest.mark.with_core
def test_create_cannot_set_name(tmp_path: Path, offline_flake_hook: Any) -> None:
    """Template = 'default'
    # All default params
    """
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template="default",  # The default template currently has a non-writable 'name'
        initial={
            "name": "test-clan",
        },
        _postprocess_flake_hook=offline_flake_hook,
    )
    with pytest.raises(ClanError) as exc_info:
        create_clan(opts)

    assert (
        "Key 'meta.name' is not writeable. It seems its value is statically defined in nix."
        in str(exc_info.value)
    )


@pytest.mark.with_core
def test_create_invalid_name(tmp_path: Path, offline_flake_hook: Any) -> None:
    """Template = 'default'
    # All default params
    """
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template="default",  # The default template currently has a non-writable 'name'
        initial={
            "name": "test clan",  # spaces are not allowed in hostnames
        },
        _postprocess_flake_hook=offline_flake_hook,
    )
    with pytest.raises(ClanError) as exc_info:
        create_clan(opts)

    assert "must be a valid hostname." in str(exc_info.value)
    assert "name" in str(exc_info.value.location)
