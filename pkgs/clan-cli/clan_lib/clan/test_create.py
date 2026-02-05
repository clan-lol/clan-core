from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.clan.get import get_clan_details
from clan_lib.clan.update import UpdateOptions, set_clan_details
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore

if TYPE_CHECKING:
    from clan_lib.nix_models.typing import InventoryMetaInput


@pytest.mark.broken_on_darwin
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


@pytest.mark.broken_on_darwin
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


@pytest.mark.broken_on_darwin
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
            "name": "test-clan",
            "domain": "clan",
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


# All templates use {{placeholder}} syntax that gets substituted
# during creation (before git init), using the directory name by default
# TODO: Also test flake-parts templates (currently excluded - require network access)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
@pytest.mark.parametrize("template", ["default", "minimal"])
def test_create_substitutes_placeholders(
    tmp_path: Path, offline_flake_hook: Any, template: str
) -> None:
    """Test that placeholders in templates are substituted."""
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template=template,
        domain="clan",
        _postprocess_flake_hook=offline_flake_hook,
    )
    create_clan(opts)

    assert dest.exists()
    assert dest.is_dir()

    # Verify placeholders were substituted
    # Check both clan.nix and flake.nix since templates differ
    clan_nix = dest / "clan.nix"
    flake_nix = dest / "flake.nix"

    content = ""
    if clan_nix.exists():
        content += clan_nix.read_text()
    if flake_nix.exists():
        content += flake_nix.read_text()

    # Ensure placeholders were substituted
    assert "{{name}}" not in content
    assert "{{domain}}" not in content
    assert (
        'meta.name = "test_clan"' in content
        or 'meta.name = inputs.nixpkgs.lib.mkDefault "test_clan"' in content
    )
    assert (
        'meta.domain = "clan"' in content
        or 'meta.domain = inputs.nixpkgs.lib.mkDefault "clan"' in content
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_minimal_can_be_modified_by_api(
    tmp_path: Path, offline_flake_hook: Any
) -> None:
    """Test that the API can change explicit settings of the minimal template."""
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template="minimal",
        _postprocess_flake_hook=offline_flake_hook,
    )
    create_clan(opts)

    assert dest.exists()
    assert dest.is_dir()

    flake = Flake(str(dest))
    meta: InventoryMetaInput = {
        **get_clan_details(flake),
        "name": "overwritten",
        "domain": "also_overwritten",
    }
    result = set_clan_details(UpdateOptions(flake=flake, meta=meta))
    assert result["meta"]["name"] == "overwritten", (
        "Minimal template should be customizable via api"
    )
    assert result["meta"]["domain"] == "also_overwritten", (
        "Minimal template should be customizable via api"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_default_cant_be_modified_by_api(
    tmp_path: Path, offline_flake_hook: Any
) -> None:
    """Test that the default template correctly detects that it can't be modified by the API"""
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
    meta: InventoryMetaInput = {
        **get_clan_details(flake),
        "name": "overwritten",
        "domain": "also_overwritten",
    }
    with pytest.raises(ClanError) as exc_info:
        set_clan_details(UpdateOptions(flake=flake, meta=meta))
    assert "is readonly" in str(exc_info.value)


@pytest.mark.with_core
def test_create_invalid_name(tmp_path: Path, offline_flake_hook: Any) -> None:
    """Template = 'default'
    # All default params
    """
    dest = tmp_path / "test_clan"

    opts = CreateOptions(
        dest=dest,
        template="default",  # The default template currently has a non-writable 'name'
        initial={"name": "test clan", "domain": "clan"},  # spaces are not allowed
        _postprocess_flake_hook=offline_flake_hook,
    )
    with pytest.raises(ClanError) as exc_info:
        create_clan(opts)

    assert "must be a valid hostname." in str(exc_info.value)
    assert "name" in str(exc_info.value.location)
