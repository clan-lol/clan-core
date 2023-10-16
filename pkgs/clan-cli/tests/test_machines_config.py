from fixtures_flakes import FlakeForTest

from clan_cli.config import machine


def test_schema_for_machine(test_flake: FlakeForTest) -> None:
    schema = machine.schema_for_machine(test_flake.name, "machine1")
    assert "properties" in schema
