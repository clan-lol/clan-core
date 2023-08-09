from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from environment import mock_env
from secret_cli import SecretCli

if TYPE_CHECKING:
    from test_keys import KeyPair


def test_import_sops(
    test_root: Path,
    clan_flake: Path,
    capsys: pytest.CaptureFixture,
    test_keys: list["KeyPair"],
) -> None:
    cli = SecretCli()

    with mock_env(SOPS_AGE_KEY=test_keys[1].privkey):
        cli.run(["machines", "add", "machine1", test_keys[0].pubkey])
        cli.run(["users", "add", "user1", test_keys[1].pubkey])
        cli.run(["users", "add", "user2", test_keys[2].pubkey])
        cli.run(["groups", "add-user", "group1", "user1"])
        cli.run(["groups", "add-user", "group1", "user2"])

        # To edit:
        # SOPS_AGE_KEY=AGE-SECRET-KEY-1U5ENXZQAY62NC78Y2WC0SEGRRMAEEKH79EYY5TH4GPFWJKEAY0USZ6X7YQ sops --age age14tva0txcrl0zes05x7gkx56qd6wd9q3nwecjac74xxzz4l47r44sv3fz62 ./data/secrets.yaml
        cli.run(
            [
                "import-sops",
                "--group",
                "group1",
                "--machine",
                "machine1",
                str(test_root.joinpath("data", "secrets.yaml")),
            ]
        )
        capsys.readouterr()
        cli.run(["users", "list"])
        users = sorted(capsys.readouterr().out.rstrip().split())
        assert users == ["user1", "user2"]

        capsys.readouterr()
        cli.run(["get", "secret-key"])
        assert capsys.readouterr().out == "secret-value"
