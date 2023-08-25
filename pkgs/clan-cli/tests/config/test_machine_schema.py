import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from clan_cli.config import machine

CLAN_NIXPKGS = os.environ.get("CLAN_NIXPKGS", "")
if CLAN_NIXPKGS == "":
    raise Exception("CLAN_NIXPKGS not set")


# fixture for the example flake located under ./example_flake
# The flake is a template that is copied to a temporary location.
# Variables like __CLAN_NIXPKGS__ are replaced with the value of the
# CLAN_NIXPKGS environment variable.
@pytest.fixture
def flake_dir() -> Generator[Path, None, None]:
    template = Path(__file__).parent / "example_flake"
    # copy the template to a new temporary location
    with tempfile.TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        for path in template.glob("**/*"):
            if path.is_dir():
                (tmpdir / path.relative_to(template)).mkdir()
            else:
                (tmpdir / path.relative_to(template)).write_text(path.read_text())
        # in the flake.nix file replace the string __CLAN_URL__ with the the clan flake
        # provided by get_clan_flake_toplevel
        flake_nix = tmpdir / "flake.nix"
        flake_nix.write_text(
            flake_nix.read_text().replace("__CLAN_NIXPKGS__", CLAN_NIXPKGS)
        )
        yield tmpdir


def test_schema_for_machine(
    flake_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    schema = machine.schema_for_machine("machine1", flake_dir)
    assert "properties" in schema
