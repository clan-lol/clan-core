# ruff: noqa: SLF001
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from clan_lib.errors import ClanError
from clan_lib.nix import nix_eval
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import delete_by_path, set_value_by_path


class MockFlake:
    def __init__(self, default: Path) -> None:
        f = default
        assert f.exists(), f"File {f} does not exist"
        self._file = f

    def invalidate_cache(self) -> None:
        pass

    def select(
        self,
        selector: str,
        nix_options: list[str] | None = None,
    ) -> Any:
        del nix_options  # Unused but kept for API compatibility
        nixpkgs = os.environ.get("NIXPKGS")
        select = os.environ.get("NIX_SELECT")
        clan_core_path = os.environ.get("CLAN_CORE_PATH")

        assert nixpkgs, "NIXPKGS environment variable is not set"
        assert select, "NIX_SELECT environment variable is not set"
        assert clan_core_path, "CLAN_CORE_PATH environment variable is not set"

        cmd = nix_eval(
            [
                "--impure",
                "--expr",
                f"""
            let
                pkgs = import {nixpkgs} {{}};
                inherit (pkgs) lib;
                clanLib = import {Path(clan_core_path)}/lib {{ inherit lib; self = null; nixpkgs = {nixpkgs}; }};
                select = (import {select}/select.nix).select;
                result = import {self._file} {{ inherit pkgs lib clanLib; }};
            in
                select "{selector}" result
            """,
            ],
        )
        output = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
        )
        res_str = output.stdout.decode()

        if output.returncode != 0:
            msg = f"Failed to evaluate {selector} in {self._file}: {output.stderr.decode()}"
            raise ClanError(msg)
        return json.loads(res_str)

    @property
    def path(self) -> Path:
        return self._file.parent


folder_path = Path(__file__).parent.resolve()


@pytest.fixture
def setup_test_files(tmp_path: Path, request: pytest.FixtureRequest) -> Path:
    entry_file = request.param  # e.g., "1.nix"
    inventory_file = entry_file.replace(".nix", ".json")

    nix_src = folder_path / "fixtures" / entry_file
    json_src = folder_path / "fixtures" / inventory_file

    nix_dst = tmp_path / entry_file
    json_dst = tmp_path / inventory_file

    shutil.copyfile(nix_src, nix_dst)
    shutil.copyfile(json_src, json_dst)

    return tmp_path


@pytest.mark.with_core
@pytest.mark.parametrize("setup_test_files", ["1.nix"], indirect=True)
def test_simple_read_write(setup_test_files: Path) -> None:
    files = list(setup_test_files.iterdir())
    nix_file = next(f for f in files if f.suffix == ".nix")
    json_file = next(f for f in files if f.suffix == ".json")

    assert nix_file.exists()
    assert json_file.exists()

    store = InventoryStore(
        flake=MockFlake(nix_file),
        inventory_file_name=json_file.name,
        _keys=["foo", "protected"],
    )
    store._flake.invalidate_cache()
    data: dict = store.read()  # type: ignore
    assert data == {"foo": "bar", "protected": "protected"}

    set_value_by_path(data, "foo", "foo")  # type: ignore
    store.write(data, "test", commit=False)  # type: ignore
    # Default method to access the inventory
    assert store.read() == {"foo": "foo", "protected": "protected"}

    # Test the data is actually persisted
    assert store._get_persisted() == {"foo": "foo"}

    # clan_lib.errors.ClanError: Key 'protected' is not writeable.
    invalid_data = {"protected": "foo"}
    with pytest.raises(ClanError) as e:
        store.write(invalid_data, "test", commit=False)  # type: ignore
    assert (
        str(e.value)
        == "Key 'protected' is not writeable. It seems its value is statically defined in nix."
    )

    # Test the data is not touched
    assert store.read() == data
    assert store._get_persisted() == {"foo": "foo"}

    # Remove the foo key from the persisted data
    # Technically data = { } should also work
    data = {"protected": "protected"}
    store.write(data, "test", commit=False)  # type: ignore


@pytest.mark.with_core
@pytest.mark.parametrize("setup_test_files", ["deferred.nix"], indirect=True)
def test_simple_deferred(setup_test_files: Path) -> None:
    files = list(setup_test_files.iterdir())
    nix_file = next(f for f in files if f.suffix == ".nix")
    json_file = next(f for f in files if f.suffix == ".json")

    assert nix_file.exists()
    assert json_file.exists()

    store = InventoryStore(
        flake=MockFlake(nix_file),
        inventory_file_name=json_file.name,
        # Needed to allow auto-transforming deferred modules
        _allowed_path_transforms=["foo.*"],
        _keys=["foo"],  # disable toplevel filtering
    )

    data = store.read()
    assert data == {"foo": {"a": {}, "b": {}}}

    # Create a new "deferredModule" "C"
    set_value_by_path(data, "foo.c", {})
    store.write(data, "test", commit=False)  # type: ignore

    assert store.read() == {"foo": {"a": {}, "b": {}, "c": {}}}

    # Remove the "deferredModule" "C"
    delete_by_path(data, "foo.c")  # type: ignore
    store.write(data, "test", commit=False)
    assert store.read() == {"foo": {"a": {}, "b": {}}}

    # Write settings into a new "deferredModule" "C" and read them back
    set_value_by_path(data, "foo.c", {"timeout": "1s"})
    store.write(data, "test", commit=False)  # type: ignore

    assert store.read() == {"foo": {"a": {}, "b": {}, "c": {"timeout": "1s"}}}

    # Remove the "deferredModle" "C" along with its settings
    delete_by_path(data, "foo.c")  # type: ignore
    store.write(data, "test", commit=False)
    assert store.read() == {"foo": {"a": {}, "b": {}}}


# TODO: Add this feature. We want it, but its more complex than expected.
# @pytest.mark.with_core
# @pytest.mark.parametrize("setup_test_files", ["deferred.nix"], indirect=True)
# def test_conflicts_deferred(setup_test_files: Path) -> None:
#     files = list(setup_test_files.iterdir())
#     nix_file = next(f for f in files if f.suffix == ".nix")
#     json_file = next(f for f in files if f.suffix == ".json")

#     assert nix_file.exists()
#     assert json_file.exists()

#     store = InventoryStore(
#         flake=MockFlake(nix_file),
#         inventory_file_name=json_file.name,
#         # Needed to allow auto-transforming deferred modules
#         _allowed_path_transforms=["foo.*"],
#         _keys=[],  # disable toplevel filtering
#     )

#     data = store.read()
#     assert data == {"foo": {"a": {}, "b": {}}}

#     # Create a new "deferredModule" "a" which collides with existing foo.a
#     set_value_by_path(data, "foo.a", {"timeout": "1s"})  # type: ignore
#     with pytest.raises(ClanError) as e:
#         store.write(data, "test", commit=False)
#     assert (
#         str(e.value)
#         == "Key 'foo.a' is not writeable. It seems its value is statically defined in nix."
#     )

#     # Giving an empty value to a deferred module does not throw an error
#     # This is deduplicated with the module in nix and does not need to create a new module
#     set_value_by_path(data, "foo.a", {})
#     store.write(data, "test", commit=False)
#     # unchanged data
#     assert store.read() == {"foo": {"a": {}, "b": {}}}


@pytest.mark.with_core
@pytest.mark.parametrize("setup_test_files", ["lists.nix"], indirect=True)
def test_manipulate_list(setup_test_files: Path) -> None:
    files = list(setup_test_files.iterdir())
    nix_file = next(f for f in files if f.suffix == ".nix")
    json_file = next(f for f in files if f.suffix == ".json")

    assert nix_file.exists()
    assert json_file.exists()

    store = InventoryStore(
        flake=MockFlake(nix_file),
        inventory_file_name=json_file.name,
        _keys=["empty", "predefined"],
    )

    data = store.read()

    # [a, b] are static items in the list
    assert data == {"empty": [], "predefined": ["a", "b"]}

    # Add a new item to the list
    set_value_by_path(data, "predefined", ["a", "b", "c"])
    store.write(data, "test", commit=False)

    assert store.read() == {"empty": [], "predefined": ["c", "a", "b"]}

    # Remove an item from the list
    set_value_by_path(data, "predefined", ["a", "b"])
    store.write(data, "test", commit=False)
    assert store.read() == {"empty": [], "predefined": ["a", "b"]}

    # Test adding more than one of the same item
    set_value_by_path(data, "empty", ["a", "b", "a"])

    with pytest.raises(ClanError) as e:
        store.write(data, "test", commit=False)
    assert (
        str(e.value)
        == "Key 'empty' contains list duplicates: ['a'] - List values must be unique."
    )

    assert store.read() == {"empty": [], "predefined": ["a", "b"]}


@pytest.mark.with_core
@pytest.mark.parametrize("setup_test_files", ["lists.nix"], indirect=True)
def test_static_list_items(setup_test_files: Path) -> None:
    files = list(setup_test_files.iterdir())
    nix_file = next(f for f in files if f.suffix == ".nix")
    json_file = next(f for f in files if f.suffix == ".json")

    assert nix_file.exists()
    assert json_file.exists()

    store = InventoryStore(
        flake=MockFlake(nix_file),
        inventory_file_name=json_file.name,
        _keys=["empty", "predefined"],
    )

    data = store.read()
    assert data == {"empty": [], "predefined": ["a", "b"]}

    # Removing a nix defined item from the list throws an error
    set_value_by_path(data, "predefined", ["b"])
    with pytest.raises(ClanError) as e:
        store.write(data, "test", commit=False)

    assert (
        str(e.value)
        == "Key 'predefined' doesn't contain items ['a'] - Deleting them is not possible, they are static values set via a .nix file"
    )
