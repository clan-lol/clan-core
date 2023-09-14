from pathlib import Path

from clan_cli.config import machine


def test_schema_for_machine(clan_flake: Path) -> None:
    schema = machine.schema_for_machine("machine1", clan_flake)
    assert "properties" in schema
