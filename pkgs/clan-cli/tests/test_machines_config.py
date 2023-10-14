from fixtures_flakes import TestFlake

from clan_cli.config import machine


def test_schema_for_machine(test_flake: TestFlake) -> None:
    schema = machine.schema_for_machine(test_flake.name, "machine1")
    assert "properties" in schema
