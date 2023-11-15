import pytest
from fixtures_flakes import FlakeForTest

from clan_cli.config.schema import machine_schema


@pytest.mark.with_core
def test_schema_for_machine(test_flake_with_core: FlakeForTest) -> None:
    schema = machine_schema(test_flake_with_core.path, config={})
    assert "properties" in schema
