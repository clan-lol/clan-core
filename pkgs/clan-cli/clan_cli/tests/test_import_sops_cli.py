from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput

if TYPE_CHECKING:
    from .age_keys import KeyPair


def test_import_sops(
    test_root: Path,
    test_flake: FlakeForTest,
    capture_output: CaptureOutput,
    monkeypatch: pytest.MonkeyPatch,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[1].privkey)
    cli.run(
        [
            "secrets",
            "machines",
            "add",
            "--flake",
            str(test_flake.path),
            "machine1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake.path),
            "user1",
            age_keys[1].pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake.path),
            "user2",
            age_keys[2].pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake.path),
            "group1",
            "user1",
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake.path),
            "group1",
            "user2",
        ]
    )

    # To edit:
    # SOPS_AGE_KEY=AGE-SECRET-KEY-1U5ENXZQAY62NC78Y2WC0SEGRRMAEEKH79EYY5TH4GPFWJKEAY0USZ6X7YQ sops --age age14tva0txcrl0zes05x7gkx56qd6wd9q3nwecjac74xxzz4l47r44sv3fz62 ./data/secrets.yaml
    cmd = [
        "secrets",
        "import-sops",
        "--flake",
        str(test_flake.path),
        "--group",
        "group1",
        "--machine",
        "machine1",
        str(test_root.joinpath("data", "secrets.yaml")),
    ]

    cli.run(cmd)
    with capture_output as output:
        cli.run(["secrets", "users", "list", "--flake", str(test_flake.path)])
    users = sorted(output.out.rstrip().split())
    assert users == ["user1", "user2"]

    with capture_output as output:
        cli.run(["secrets", "get", "--flake", str(test_flake.path), "secret-key"])
    assert output.out == "secret-value"
