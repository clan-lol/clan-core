from unittest.mock import Mock

from clan_lib.vars.generator import (
    Generator,
    GeneratorKey,
)
from clan_lib.vars.graph import all_missing_closure, requested_closure


def generator_names(generator: list[Generator]) -> list[str]:
    return [gen.name for gen in generator]


def generator_keys(generator: list[Generator]) -> set[GeneratorKey]:
    return {gen.key for gen in generator}


def create_mock_stores(exists_map: dict[str, bool]) -> tuple[Mock, Mock]:
    """Create mock public and secret stores with specified existence mapping."""
    public_store = Mock()
    secret_store = Mock()

    def mock_exists(generator: Generator, _file_name: str) -> bool:
        return exists_map.get(generator.name, False)

    def mock_hash_valid(generator: Generator) -> bool:
        return exists_map.get(generator.name, False)

    public_store.exists.side_effect = mock_exists
    secret_store.exists.side_effect = mock_exists
    public_store.hash_is_valid.side_effect = mock_hash_valid
    secret_store.hash_is_valid.side_effect = mock_hash_valid

    return public_store, secret_store


def test_required_generators() -> None:
    # Create mock stores
    exists_map = {
        "gen_1": True,
        "gen_2": False,
        "gen_2a": False,
        "gen_2b": True,
    }
    public_store, secret_store = create_mock_stores(exists_map)

    # Create generators with proper machine context
    machine_name = "test_machine"
    gen_1 = Generator(
        name="gen_1",
        dependencies=[],
        machines=[machine_name],
        _public_store=public_store,
        _secret_store=secret_store,
    )
    gen_2 = Generator(
        name="gen_2",
        dependencies=[gen_1.key],
        machines=[machine_name],
        _public_store=public_store,
        _secret_store=secret_store,
    )
    gen_2a = Generator(
        name="gen_2a",
        dependencies=[gen_2.key],
        machines=[machine_name],
        _public_store=public_store,
        _secret_store=secret_store,
    )
    gen_2b = Generator(
        name="gen_2b",
        dependencies=[gen_2.key],
        machines=[machine_name],
        _public_store=public_store,
        _secret_store=secret_store,
    )
    generators: dict[GeneratorKey, Generator] = {
        generator.key: generator for generator in [gen_1, gen_2, gen_2a, gen_2b]
    }

    assert generator_names(requested_closure([gen_1.key], generators)) == [
        "gen_1",
        "gen_2",
        "gen_2a",
        "gen_2b",
    ]
    assert generator_names(requested_closure([gen_2.key], generators)) == [
        "gen_2",
        "gen_2a",
        "gen_2b",
    ]
    assert generator_names(requested_closure([gen_2a.key], generators)) == [
        "gen_2",
        "gen_2a",
        "gen_2b",
    ]
    assert generator_names(requested_closure([gen_2b.key], generators)) == [
        "gen_2",
        "gen_2a",
        "gen_2b",
    ]

    assert generator_names(all_missing_closure(generators.keys(), generators)) == [
        "gen_2",
        "gen_2a",
        "gen_2b",
    ]


def test_shared_generator_invalidates_multiple_machines_dependents() -> None:
    # Create mock stores
    exists_map = {"shared_gen": False, "gen_1": True, "gen_2": True}
    public_store, secret_store = create_mock_stores(exists_map)

    # Create generators with proper machine context
    machine_1 = "machine_1"
    machine_2 = "machine_2"
    shared_gen = Generator(
        name="shared_gen",
        dependencies=[],
        share=True,  # Mark as shared generator
        machines=[machine_1, machine_2],  # Shared across both machines
        _public_store=public_store,
        _secret_store=secret_store,
    )
    gen_1 = Generator(
        name="gen_1",
        dependencies=[shared_gen.key],
        machines=[machine_1],
        _public_store=public_store,
        _secret_store=secret_store,
    )
    gen_2 = Generator(
        name="gen_2",
        dependencies=[shared_gen.key],
        machines=[machine_2],
        _public_store=public_store,
        _secret_store=secret_store,
    )
    generators: dict[GeneratorKey, Generator] = {
        generator.key: generator for generator in [shared_gen, gen_1, gen_2]
    }

    assert generator_keys(all_missing_closure(generators.keys(), generators)) == {
        GeneratorKey(name="shared_gen", machine=None),
        GeneratorKey(name="gen_1", machine=machine_1),
        GeneratorKey(name="gen_2", machine=machine_2),
    }, (
        "All generators should be included in all_missing_closure due to shared dependency"
    )

    assert generator_keys(requested_closure([shared_gen.key], generators)) == {
        GeneratorKey(name="shared_gen", machine=None),
        GeneratorKey(name="gen_1", machine=machine_1),
        GeneratorKey(name="gen_2", machine=machine_2),
    }, "All generators should be included in requested_closure due to shared dependency"
