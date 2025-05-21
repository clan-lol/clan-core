# ruff: noqa: SLF001
import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from clan_lib.errors import ClanError
from clan_lib.persist.inventory_store import InventoryStore


class MockFlake:
    def __init__(self, default: Path) -> None:
        f = default
        assert f.exists(), f"File {f} does not exist"
        self._file = f

    def select(
        self,
        selector: str,
        nix_options: list[str] | None = None,
    ) -> Any:
        nixpkgs = os.environ.get("NIXPKGS")
        select = os.environ.get("NIX_SELECT")
        clan_core_path = os.environ.get("CLAN_CORE_PATH")

        assert nixpkgs, "NIXPKGS environment variable is not set"
        assert select, "NIX_SELECT environment variable is not set"
        assert clan_core_path, "CLAN_CORE_PATH environment variable is not set"

        output = subprocess.run(
            [
                "nix",
                "eval",
                "--impure",
                "--json",
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


def test_for_johannes() -> None:
    nix_file = folder_path / "fixtures/1.nix"
    json_file = folder_path / "fixtures/1.json"
    with TemporaryDirectory() as tmp:
        shutil.copyfile(
            str(nix_file),
            str(Path(tmp) / "1.nix"),
        )
        shutil.copyfile(
            str(json_file),
            str(Path(tmp) / "1.json"),
        )

        store = InventoryStore(
            flake=MockFlake(Path(tmp) / "1.nix"),
            inventory_file_name="1.json",
        )
        assert store.read() == {"foo": "bar", "protected": "protected"}

        data = {"foo": "foo"}
        store.write(data, "test", commit=False)  # type: ignore
        # Default method to access the inventory
        assert store.read() == {"foo": "foo", "protected": "protected"}

        # Test the data is actually persisted
        assert store._get_persisted() == data

        # clan_lib.errors.ClanError: Key 'protected' is not writeable.
        invalid_data = {"protected": "foo"}
        with pytest.raises(ClanError) as e:
            store.write(invalid_data, "test", commit=False)  # type: ignore
        assert str(e.value) == "Key 'protected' is not writeable."

        # Test the data is not touched
        assert store.read() == {"foo": "foo", "protected": "protected"}
        assert store._get_persisted() == data

        # Remove the foo key from the persisted data
        # Technically data = { } should also work
        data = {"protected": "protected"}
        store.write(data, "test", commit=False)  # type: ignore
