from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fixtures_flakes import generate_flake
from helpers.cli import Cli
from root import CLAN_CORE

if TYPE_CHECKING:
    pass


@pytest.mark.impure
def test_generate_secret(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    # age_keys: list["KeyPair"],
) -> None:
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(
            my_machine=dict(
                clan=dict(
                    core=dict(
                        vars=dict(
                            generators=dict(
                                my_generator=dict(
                                    files=dict(
                                        my_secret=dict(
                                            secret=False,
                                        )
                                    ),
                                    script="echo hello > $out/my_secret",
                                )
                            )
                        )
                    )
                )
            )
        ),
    )
    monkeypatch.chdir(flake.path)
    cli = Cli()
    cmd = ["vars", "generate", "--flake", str(flake.path), "my_machine"]
    cli.run(cmd)
    assert (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    ).is_file()
