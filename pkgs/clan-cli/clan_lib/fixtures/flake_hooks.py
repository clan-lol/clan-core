from collections.abc import Callable
from pathlib import Path

import pytest
from clan_lib.cmd import RunOpts, run
from clan_lib.nix import nix_command


def substitute_flake_inputs(clan_dir: Path, clan_core_path: Path) -> None:
    flake_nix = clan_dir / "flake.nix"
    assert flake_nix.exists()

    content = flake_nix.read_text()
    content = content.replace(
        "https://git.clan.lol/clan/clan-core/archive/main.tar.gz",
        f"path://{clan_core_path}",
    )
    flake_nix.write_text(content)

    run(nix_command(["flake", "update"]), RunOpts(cwd=clan_dir))

    flake_lock = clan_dir / "flake.lock"
    assert flake_lock.exists(), "flake.lock should exist after flake update"


@pytest.fixture
def offline_flake_hook(clan_core: Path) -> Callable[[Path], None]:
    def patch(clan_dir: Path) -> None:
        substitute_flake_inputs(clan_dir, clan_core)

    return patch


@pytest.fixture(scope="session")
def offline_session_flake_hook(clan_core: Path) -> Callable[[Path], None]:
    def patch(clan_dir: Path) -> None:
        substitute_flake_inputs(clan_dir, clan_core)

    return patch
