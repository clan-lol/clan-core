import fileinput
import shutil
import tempfile
from pathlib import Path
from typing import Iterator

import pytest
from root import CLAN_CORE

from clan_cli.dirs import nixpkgs_source


# substitutes string sin a file.
# This can be used on the flake.nix or default.nix of a machine
def substitute(
    file: Path,
    clan_core_flake: Path | None = None,
    flake: Path = Path(__file__).parent,
) -> None:
    sops_key = str(flake.joinpath("sops.key"))
    for line in fileinput.input(file, inplace=True):
        line = line.replace("__NIXPKGS__", str(nixpkgs_source()))
        if clan_core_flake:
            line = line.replace("__CLAN_CORE__", str(clan_core_flake))
        line = line.replace("__CLAN_SOPS_KEY_PATH__", sops_key)
        line = line.replace("__CLAN_SOPS_KEY_DIR__", str(flake))
        print(line, end="")


def create_flake(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    clan_core_flake: Path | None = None,
    machines: list[str] = [],
    remote: bool = False,
) -> Iterator[Path]:
    """
    Creates a flake with the given name and machines.
    The machine names map to the machines in ./test_machines
    """
    template = Path(__file__).parent / name
    # copy the template to a new temporary location
    with tempfile.TemporaryDirectory() as tmpdir_:
        home = Path(tmpdir_)
        flake = home / name
        shutil.copytree(template, flake)
        # lookup the requested machines in ./test_machines and include them
        if machines:
            (flake / "machines").mkdir(parents=True, exist_ok=True)
        for machine_name in machines:
            machine_path = Path(__file__).parent / "machines" / machine_name
            shutil.copytree(machine_path, flake / "machines" / machine_name)
            substitute(flake / "machines" / machine_name / "default.nix", flake)
        # in the flake.nix file replace the string __CLAN_URL__ with the the clan flake
        # provided by get_test_flake_toplevel
        flake_nix = flake / "flake.nix"
        # this is where we would install the sops key to, when updating
        substitute(flake_nix, clan_core_flake, flake)
        if remote:
            with tempfile.TemporaryDirectory() as workdir:
                monkeypatch.chdir(workdir)
                monkeypatch.setenv("HOME", str(home))
                yield flake
        else:
            monkeypatch.chdir(flake)
            monkeypatch.setenv("HOME", str(home))
            yield flake


@pytest.fixture
def test_flake(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    yield from create_flake(monkeypatch, "test_flake")


@pytest.fixture
def test_flake_with_core(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    if not (CLAN_CORE / "flake.nix").exists():
        raise Exception(
            "clan-core flake not found. This test requires the clan-core flake to be present"
        )
    yield from create_flake(monkeypatch, "test_flake_with_core", CLAN_CORE)


@pytest.fixture
def test_flake_with_core_and_pass(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    if not (CLAN_CORE / "flake.nix").exists():
        raise Exception(
            "clan-core flake not found. This test requires the clan-core flake to be present"
        )
    yield from create_flake(monkeypatch, "test_flake_with_core_and_pass", CLAN_CORE)
