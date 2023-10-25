from pathlib import Path

from clan_cli.config import machine


def test_schema_for_machine(test_flake: Path) -> None:
    schema = machine.schema_for_machine("machine1", flake=test_flake)
    assert "properties" in schema
