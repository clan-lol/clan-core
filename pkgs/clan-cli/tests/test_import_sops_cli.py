from pathlib import Path
from typing import TYPE_CHECKING
from fixtures_flakes import FlakeForTest
from clan_cli.debug import repro_env_break

import pytest
from cli import Cli

if TYPE_CHECKING:
    from age_keys import KeyPair


def test_import_sops(
    test_root: Path,
    test_flake: FlakeForTest,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    age_keys: list["KeyPair"],
) -> None:
    cli = Cli()

    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[1].privkey)
    cli.run(["secrets", "machines", "add", "machine1", age_keys[0].pubkey, test_flake.name])
    cli.run(["secrets", "users", "add", "user1", age_keys[1].pubkey, test_flake.name])
    cli.run(["secrets", "users", "add", "user2", age_keys[2].pubkey, test_flake.name])
    cli.run(["secrets", "groups", "add-user", "group1", "user1", test_flake.name])
    cli.run(["secrets", "groups", "add-user", "group1", "user2", test_flake.name])

    # To edit:
    # SOPS_AGE_KEY=AGE-SECRET-KEY-1U5ENXZQAY62NC78Y2WC0SEGRRMAEEKH79EYY5TH4GPFWJKEAY0USZ6X7YQ sops --age age14tva0txcrl0zes05x7gkx56qd6wd9q3nwecjac74xxzz4l47r44sv3fz62 ./data/secrets.yaml
    cmd = [
            "secrets",
            "import-sops",
            "--group",
            "group1",
            "--machine",
            "machine1",
            str(test_root.joinpath("data", "secrets.yaml")),
            test_flake.name
        ]
    repro_env_break(work_dir=test_flake.path, cmd=cmd)
    cli.run(
        cmd
    )
    capsys.readouterr()
    cli.run(["secrets", "users", "list", test_flake.name])
    users = sorted(capsys.readouterr().out.rstrip().split())
    assert users == ["user1", "user2"]

    capsys.readouterr()
    cli.run(["secrets", "get", "secret-key", test_flake.name])
    assert capsys.readouterr().out == "secret-value"
