import shutil
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.flake.flake import Flake


@pytest.fixture(scope="session")
def offline_template(tmp_path_factory: Any, offline_session_flake_hook: Any) -> Path:
    base_tmp = tmp_path_factory.mktemp("minimal-clan-template")
    template = Path(__file__).parent / Path("lib_clan")
    dst_dir = base_tmp / "offline"

    shutil.copytree(template, dst_dir, dirs_exist_ok=True, symlinks=True)

    # Emtpy clan.nix file for evaluation of the template
    clan_file = dst_dir / "clan.nix"
    with (clan_file).open("w") as f:
        f.write(r"""{ }""")

    # expensive call ~6 seconds
    # Run in session scope to avoid repeated calls
    offline_session_flake_hook(dst_dir)

    return dst_dir


@pytest.fixture()
def patch_clan_template(monkeypatch: Any, offline_template: Path) -> None:
    @contextmanager
    def fake_clan_template(
        flake: Flake,
        template_ident: str,
        dst_dir: Path,
        post_process: Callable[[Path], None] | None = None,
    ) -> Iterator[Path]:
        # Just yield static destination directory without any processing
        shutil.copytree(offline_template, dst_dir, dirs_exist_ok=True, symlinks=True)
        yield dst_dir

    monkeypatch.setattr("clan_lib.clan.create.clan_template", fake_clan_template)


@pytest.fixture()
def clan_flake(tmp_path: Path, patch_clan_template: Any) -> Callable[[str], Flake]:
    def factory(clan_expr: str) -> Flake:
        # TODO: Make more options configurable
        dest = tmp_path / "my-clan"
        opts = CreateOptions(
            dest,
            template="minimal",  # Has no effect, since we patch the clan_template
            update_clan=False,  # Takes ~6 seconds, generate a static lockfile per session.
        )
        create_clan(opts)

        with (dest / "clan.nix").open("w") as f:
            f.write(clan_expr)

        return Flake(str(dest))

    return factory
