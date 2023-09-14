import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from clan_cli.dirs import nixpkgs_source


@pytest.fixture(scope="module")
def monkeymodule() -> Generator[pytest.MonkeyPatch, None, None]:
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="module")
def clan_flake(monkeymodule: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    template = Path(__file__).parent / "clan_flake"
    # copy the template to a new temporary location
    with tempfile.TemporaryDirectory() as tmpdir_:
        home = Path(tmpdir_)
        flake = home / "clan_flake"
        shutil.copytree(template, flake)
        # in the flake.nix file replace the string __CLAN_URL__ with the the clan flake
        # provided by get_clan_flake_toplevel
        flake_nix = flake / "flake.nix"
        flake_nix.write_text(
            flake_nix.read_text().replace("__NIXPKGS__", str(nixpkgs_source()))
        )
        # check that an empty config is returned if no json file exists
        monkeymodule.chdir(flake)
        monkeymodule.setenv("HOME", str(home))
        yield flake
