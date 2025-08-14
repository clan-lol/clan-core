from pathlib import Path

import pytest
from clan_lib.errors import ClanError

from clan_cli.tests import fixtures_flakes
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


def list_basic(
    temporary_home: Path,
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])

    assert "vm1" in output.out
    assert "vm2" in output.out


@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        {
            "inventory_expr": r"""{
                machines = {
                  web-server = {
                    tags = [ "web" "production" ];
                    description = "Production web server";
                  };
                  db-server = {
                    tags = [ "database" "production" ];
                    description = "Production database server";
                  };
                  dev-machine = {
                    tags = [ "development" ];
                    description = "Development machine";
                  };
                  backup-server = {
                    tags = [ "backup" "production" ];
                    description = "Backup server";
                  };
                };
            }"""
        },
    ],
    indirect=True,
)
def list_with_tags_single_tag(
    temporary_home: Path,
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "production",
            ]
        )

    assert "web-server" in output.out
    assert "db-server" in output.out
    assert "backup-server" in output.out
    assert "dev-machine" not in output.out


@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        {
            "inventory_expr": r"""{
                machines = {
                  web-server = {
                    tags = [ "web" "production" ];
                    description = "Production web server";
                  };
                  db-server = {
                    tags = [ "database" "production" ];
                    description = "Production database server";
                  };
                  dev-machine = {
                    tags = [ "development" ];
                    description = "Development machine";
                  };
                  backup-server = {
                    tags = [ "backup" "production" ];
                    description = "Backup server";
                  };
                };
            }"""
        },
    ],
    indirect=True,
)
def list_with_tags_multiple_tags_intersection(
    temporary_home: Path,
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "web",
                "production",
            ]
        )

    # Should only include machines that have BOTH tags (intersection)
    assert "web-server" in output.out
    # Should not include machines that have only one of the tags (intersection)
    assert "db-server" not in output.out
    assert "backup-server" not in output.out
    assert "dev-machine" not in output.out


@pytest.mark.impure
def test_machines_list_with_tags_no_matches(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "nonexistent",
            ]
        )

    assert output.out.strip() == ""


@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        {
            "inventory_expr": r"""{
                machines = {
                  server1 = {
                    tags = [ "web" ];
                  };
                  server2 = {
                    tags = [ "database" ];
                  };
                  server3 = {
                    tags = [ "web" "database" ];
                  };
                  server4 = { };
                };
            }"""
        },
    ],
    indirect=True,
)
def list_with_tags_various_scenarios(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "web",
            ]
        )

    assert "server1" in output.out
    assert "server3" in output.out
    assert "server2" not in output.out
    assert "server4" not in output.out

    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "database",
            ]
        )

    assert "server2" in output.out
    assert "server3" in output.out
    assert "server1" not in output.out
    assert "server4" not in output.out

    # Test intersection
    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "web",
                "database",
            ]
        )

    assert "server3" in output.out
    assert "server1" not in output.out
    assert "server2" not in output.out
    assert "server4" not in output.out


def created_machine_and_tags(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    cli.run(
        [
            "machines",
            "create",
            "--flake",
            str(test_flake_with_core.path),
            "test-machine",
            "--tags",
            "test",
            "server",
        ]
    )

    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])

    assert "test-machine" in output.out
    assert "vm1" in output.out
    assert "vm2" in output.out

    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "test",
            ]
        )

    assert "test-machine" in output.out
    assert "vm1" not in output.out
    assert "vm2" not in output.out

    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "server",
            ]
        )

    assert "test-machine" in output.out
    assert "vm1" not in output.out
    assert "vm2" not in output.out

    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "test",
                "server",
            ]
        )

    assert "test-machine" in output.out
    assert "vm1" not in output.out
    assert "vm2" not in output.out


@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        {
            "inventory_expr": r"""{
                machines = {
                  machine-with-tags = {
                    tags = [ "tag1" "tag2" "tag3" ];
                  };
                  machine-without-tags = { };
                };
            }"""
        },
    ],
    indirect=True,
)
def list_mixed_tagged_untagged(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])

    assert "machine-with-tags" in output.out
    assert "machine-without-tags" in output.out

    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "tag1",
            ]
        )

    assert "machine-with-tags" in output.out
    assert "machine-without-tags" not in output.out

    with capture_output as output:
        cli.run(
            [
                "machines",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "--tags",
                "nonexistent",
            ]
        )

    assert "machine-with-tags" not in output.out
    assert "machine-without-tags" not in output.out
    assert output.out.strip() == ""


def test_machines_list_require_flake_error(
    temporary_home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that machines list command fails when flake is required but not provided."""
    monkeypatch.chdir(temporary_home)
    with pytest.raises(ClanError) as exc_info:
        cli.run(["machines", "list"])

    error_message = str(exc_info.value)
    assert "flake" in error_message.lower()
