from clan_cli.vars.generator import (
    Generator,
    GeneratorKey,
)
from clan_cli.vars.graph import all_missing_closure, requested_closure


def generator_names(generator: list[Generator]) -> list[str]:
    return [gen.name for gen in generator]


def test_required_generators() -> None:
    # Create generators with proper machine context
    machine_name = "test_machine"
    gen_1 = Generator(name="gen_1", dependencies=[], machine=machine_name)
    gen_2 = Generator(
        name="gen_2",
        dependencies=[gen_1.key],
        machine=machine_name,
    )
    gen_2a = Generator(
        name="gen_2a",
        dependencies=[gen_2.key],
        machine=machine_name,
    )
    gen_2b = Generator(
        name="gen_2b",
        dependencies=[gen_2.key],
        machine=machine_name,
    )

    gen_1.exists = True
    gen_2.exists = False
    gen_2a.exists = False
    gen_2b.exists = True
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
    # Create generators with proper machine context
    machine_1 = "machine_1"
    machine_2 = "machine_2"
    shared_gen = Generator(
        name="shared_gen",
        dependencies=[],
        machine=None,  # Shared generator
    )
    gen_1 = Generator(
        name="gen_1",
        dependencies=[shared_gen.key],
        machine=machine_1,
    )
    gen_2 = Generator(
        name="gen_2",
        dependencies=[shared_gen.key],
        machine=machine_2,
    )

    shared_gen.exists = False
    gen_1.exists = True
    gen_2.exists = True
    generators: dict[GeneratorKey, Generator] = {
        generator.key: generator for generator in [shared_gen, gen_1, gen_2]
    }

    assert generator_names(all_missing_closure(generators.keys(), generators)) == [
        "shared_gen",
        "gen_1",
        "gen_2",
    ], (
        "All generators should be included in all_missing_closure due to shared dependency"
    )

    assert generator_names(requested_closure([shared_gen.key], generators)) == [
        "shared_gen",
        "gen_1",
        "gen_2",
    ], "All generators should be included in requested_closure due to shared dependency"
