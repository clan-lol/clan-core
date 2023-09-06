import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from clan_cli.dirs import nixpkgs_source

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

pytest_plugins = [
    "api",
    "temporary_dir",
    "clan_flake",
    "root",
    "age_keys",
    "sshd",
    "command",
    "ports",
    "host_group",
]


@pytest.fixture(scope="module")
def monkeymodule() -> Generator[pytest.MonkeyPatch, None, None]:
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="module")
def machine_flake(monkeymodule: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    template = Path(__file__).parent / "machine_flake"
    # copy the template to a new temporary location
    with tempfile.TemporaryDirectory() as tmpdir_:
        flake = Path(tmpdir_)
        for path in template.glob("**/*"):
            if path.is_dir():
                (flake / path.relative_to(template)).mkdir()
            else:
                (flake / path.relative_to(template)).write_text(path.read_text())
        # in the flake.nix file replace the string __CLAN_URL__ with the the clan flake
        # provided by get_clan_flake_toplevel
        flake_nix = flake / "flake.nix"
        flake_nix.write_text(
            flake_nix.read_text().replace("__NIXPKGS__", str(nixpkgs_source()))
        )
        # check that an empty config is returned if no json file exists
        monkeymodule.chdir(flake)
        yield flake
