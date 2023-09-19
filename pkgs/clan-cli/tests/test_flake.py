import fileinput
import shutil
import tempfile
from pathlib import Path
from typing import Iterator

import pytest
from root import CLAN_CORE

from clan_cli.dirs import nixpkgs_source


@pytest.fixture(scope="module")
def monkeymodule() -> Iterator[pytest.MonkeyPatch]:
    with pytest.MonkeyPatch.context() as mp:
        yield mp


def create_flake(
    monkeymodule: pytest.MonkeyPatch, name: str, clan_core_flake: Path | None = None
) -> Iterator[Path]:
    template = Path(__file__).parent / name
    # copy the template to a new temporary location
    with tempfile.TemporaryDirectory() as tmpdir_:
        home = Path(tmpdir_)
        flake = home / name
        shutil.copytree(template, flake)
        # in the flake.nix file replace the string __CLAN_URL__ with the the clan flake
        # provided by get_test_flake_toplevel
        flake_nix = flake / "flake.nix"
        for line in fileinput.input(flake_nix, inplace=True):
            line = line.replace("__NIXPKGS__", str(nixpkgs_source()))
            if clan_core_flake:
                line = line.replace("__CLAN_CORE__", str(clan_core_flake))
            print(line)
        # check that an empty config is returned if no json file exists
        monkeymodule.chdir(flake)
        monkeymodule.setenv("HOME", str(home))
        yield flake


@pytest.fixture(scope="module")
def test_flake(monkeymodule: pytest.MonkeyPatch) -> Iterator[Path]:
    yield from create_flake(monkeymodule, "test_flake")


@pytest.fixture(scope="module")
def test_flake_with_core(monkeymodule: pytest.MonkeyPatch) -> Iterator[Path]:
    if not (CLAN_CORE / "flake.nix").exists():
        raise Exception(
            "clan-core flake not found. This test requires the clan-core flake to be present"
        )
    yield from create_flake(monkeymodule, "test_flake_with_core", CLAN_CORE)
