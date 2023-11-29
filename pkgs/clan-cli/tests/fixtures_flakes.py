import fileinput
import logging
import os
import shutil
import subprocess as sp
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

import pytest
from pydantic import AnyUrl
from pydantic.tools import parse_obj_as
from root import CLAN_CORE

from clan_cli.dirs import nixpkgs_source

log = logging.getLogger(__name__)


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


class FlakeForTest(NamedTuple):
    path: Path


def create_flake(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    flake_name: str,
    clan_core_flake: Path | None = None,
    machines: list[str] = [],
    remote: bool = False,
) -> Iterator[FlakeForTest]:
    """
    Creates a flake with the given name and machines.
    The machine names map to the machines in ./test_machines
    """
    template = Path(__file__).parent / flake_name

    # copy the template to a new temporary location
    flake = temporary_home / flake_name
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

    if "/tmp" not in str(os.environ.get("HOME")):
        log.warning(
            f"!! $HOME does not point to a temp directory!! HOME={os.environ['HOME']}"
        )

    # TODO: Find out why test_vms_api.py fails in nix build
    # but works in pytest when this bottom line is commented out
    sp.run(
        ["git", "config", "--global", "init.defaultBranch", "main"],
        cwd=flake,
        check=True,
    )
    sp.run(["git", "init"], cwd=flake, check=True)
    sp.run(["git", "add", "."], cwd=flake, check=True)
    sp.run(["git", "config", "user.name", "clan-tool"], cwd=flake, check=True)
    sp.run(["git", "config", "user.email", "clan@example.com"], cwd=flake, check=True)
    sp.run(["git", "commit", "-a", "-m", "Initial commit"], cwd=flake, check=True)

    if remote:
        with tempfile.TemporaryDirectory():
            yield FlakeForTest(flake)
    else:
        yield FlakeForTest(flake)


@pytest.fixture
def test_flake(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> Iterator[FlakeForTest]:
    yield from create_flake(monkeypatch, temporary_home, "test_flake")


@pytest.fixture
def test_flake_with_core(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> Iterator[FlakeForTest]:
    if not (CLAN_CORE / "flake.nix").exists():
        raise Exception(
            "clan-core flake not found. This test requires the clan-core flake to be present"
        )
    yield from create_flake(
        monkeypatch,
        temporary_home,
        "test_flake_with_core",
        CLAN_CORE,
    )


@pytest.fixture
def test_democlan_url(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> Iterator[AnyUrl]:
    yield parse_obj_as(
        AnyUrl,
        "https://git.clan.lol/clan/democlan/archive/main.tar.gz",
    )


@pytest.fixture
def test_flake_with_core_and_pass(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> Iterator[FlakeForTest]:
    if not (CLAN_CORE / "flake.nix").exists():
        raise Exception(
            "clan-core flake not found. This test requires the clan-core flake to be present"
        )
    yield from create_flake(
        monkeypatch,
        temporary_home,
        "test_flake_with_core_and_pass",
        CLAN_CORE,
    )
