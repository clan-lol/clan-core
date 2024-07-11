import os
from pathlib import Path

import pytest
from age_keys import SopsSetup
from fixtures_flakes import generate_flake
from helpers import cli
from root import CLAN_CORE


@pytest.mark.impure
def test_generate_public_var(
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
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    secret_path = (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    )
    assert secret_path.is_file()
    assert secret_path.read_text() == "hello\n"


@pytest.mark.impure
def test_generate_secret_var(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    sops_setup: SopsSetup,
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
                                            secret=True,
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
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            os.environ.get("USER", "user"),
            sops_setup.keys[0].pubkey,
        ]
    )
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    assert not (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    ).is_file()
    assert (
        flake.path / "sops" / "secrets" / "vars-my_machine-my_generator-my_secret"
    ).is_dir()
