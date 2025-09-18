import json
import shutil
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.clan import Clan


@pytest.fixture(scope="session")
def offline_template(tmp_path_factory: Any, offline_session_flake_hook: Any) -> Path:
    base_tmp = tmp_path_factory.mktemp("minimal-clan-template")
    template = Path(__file__).parent / Path("lib_clan")
    dst_dir = base_tmp / "offline"

    shutil.copytree(template, dst_dir, dirs_exist_ok=True, symlinks=True)

    # Emtpy clan.nix file for evaluation of the template
    clan_nix_file = dst_dir / "clan.nix"
    with (clan_nix_file).open("w") as f:
        f.write(r"""{ }""")

    clan_json_file = dst_dir / "clan.json"
    with (clan_json_file).open("w") as f:
        f.write(r"""{ }""")

    inventory_json_file = dst_dir / "inventory.json"
    with (inventory_json_file).open("w") as f:
        f.write(r"""{ }""")

    # expensive call ~6 seconds
    # Run in session scope to avoid repeated calls
    offline_session_flake_hook(dst_dir)

    return dst_dir


@pytest.fixture
def patch_clan_template(monkeypatch: Any, offline_template: Path) -> None:
    @contextmanager
    def fake_clan_template(
        _flake: Flake,
        template_ident: str,  # noqa: ARG001
        dst_dir: Path,
        post_process: Callable[[Path], None] | None = None,  # noqa: ARG001
    ) -> Iterator[Path]:
        # Just yield static destination directory without any processing
        shutil.copytree(offline_template, dst_dir, dirs_exist_ok=True, symlinks=True)
        yield dst_dir

    monkeypatch.setattr("clan_lib.clan.create.clan_template", fake_clan_template)


@pytest.fixture
def clan_flake(
    tmp_path: Path,
    patch_clan_template: Any,  # noqa: ARG001
) -> Callable[[Clan | None, str | None], Flake]:
    def factory(
        clan: Clan | None = None,
        raw: str | None = None,
        mutable_inventory_json: str | None = None,
    ) -> Flake:
        # TODO: Make more options configurable
        if clan is None and raw is None:
            msg = "Either 'clan' or 'raw' must be provided to create a Flake."
            raise ValueError(msg)

        dest = tmp_path / "my-clan"
        opts = CreateOptions(
            dest,
            template="minimal",  # Has no effect, since we patch the clan_template
            update_clan=False,  # Takes ~6 seconds, generate a static lockfile per session.
        )
        create_clan(opts)

        if clan is not None:
            with (dest / "clan.json").open("w") as f:
                f.write(json.dumps(clan))

        if raw is not None:
            with (dest / "clan.nix").open("w") as f:
                f.write(raw)

        if mutable_inventory_json is not None:
            with (dest / "inventory.json").open("w") as f:
                f.write(json.dumps(mutable_inventory_json))

        return Flake(str(dest))

    return factory
