from __future__ import annotations

from graphlib import TopologicalSorter
from typing import TYPE_CHECKING

from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .generator import Generator, GeneratorKey


class GeneratorNotFoundError(ClanError):
    pass


def missing_dependency_closure(
    requested_generators: Iterable[GeneratorKey],
    generators: dict[GeneratorKey, Generator],
) -> set[GeneratorKey]:
    closure = set(requested_generators)
    # extend the graph to include all dependencies which are not on disk
    dep_closure = set()
    queue = list(closure)
    while queue:
        gen_key = queue.pop(0)

        if gen_key not in generators:
            msg = f"Requested generator {gen_key.name} not found"
            raise GeneratorNotFoundError(msg)

        for dep_key in generators[gen_key].dependencies:
            if (
                dep_key not in closure
                and dep_key in generators
                and not generators[dep_key].exists
            ):
                dep_closure.add(dep_key)
                queue.append(dep_key)
    return dep_closure


def add_missing_dependencies(
    requested_generators: Iterable[GeneratorKey],
    generators: dict[GeneratorKey, Generator],
) -> set[GeneratorKey]:
    closure = set(requested_generators)
    return missing_dependency_closure(closure, generators) | closure


def add_dependents(
    requested_generators: Iterable[GeneratorKey],
    generators: dict[GeneratorKey, Generator],
) -> set[GeneratorKey]:
    closure = set(requested_generators)
    # build reverse dependency graph (graph of dependents)
    dependents_graph: dict[GeneratorKey, set[GeneratorKey]] = {}
    for gen_key, gen in generators.items():
        for dep_key in gen.dependencies:
            if dep_key not in dependents_graph:
                dependents_graph[dep_key] = set()
            dependents_graph[dep_key].add(gen_key)
    # extend the graph to include all dependents of the current closure
    queue = list(closure)
    while queue:
        gen_key = queue.pop(0)
        for dep_key in dependents_graph.get(gen_key, []):
            if dep_key not in closure:
                closure.add(dep_key)
                queue.append(dep_key)
    return closure


def toposort_closure(
    _closure: Iterable[GeneratorKey],
    generators: dict[GeneratorKey, Generator],
) -> list[Generator]:
    closure = set(_closure)
    # return the topological sorted list of generators to execute
    final_dep_graph = {}
    for gen_key in sorted(closure, key=lambda k: (k.machine or "", k.name)):
        deps = set(generators[gen_key].dependencies) & closure
        final_dep_graph[gen_key] = deps
    sorter = TopologicalSorter(final_dep_graph)
    result = list(sorter.static_order())
    return [generators[gen_key] for gen_key in result]


# all generators in topological order
def full_closure(generators: dict[GeneratorKey, Generator]) -> list[Generator]:
    """From a set of generators, return all generators in topological order.
    This includes all dependencies and dependents of the generators.
    Returns all generators in topological order.
    """
    return toposort_closure(generators.keys(), generators)


# just the missing generators including their dependents
def all_missing_closure(generators: dict[GeneratorKey, Generator]) -> list[Generator]:
    """From a set of generators, return all incomplete generators in topological order.

    incomplete
    : A generator is missing if at least one of its files is missing.
    """
    # collect all generators that are missing from disk
    closure = {gen_key for gen_key, gen in generators.items() if not gen.exists}
    closure = add_dependents(closure, generators)
    return toposort_closure(closure, generators)


# only a selected list of generators including their missing dependencies and their dependents
def requested_closure(
    requested_generators: list[GeneratorKey],
    generators: dict[GeneratorKey, Generator],
) -> list[Generator]:
    closure = set(requested_generators)
    # extend the graph to include all dependencies which are not on disk
    closure = add_missing_dependencies(closure, generators)
    closure = add_dependents(closure, generators)
    return toposort_closure(closure, generators)


# just enough to ensure that the list of selected generators are in a consistent state.
# empty if nothing is missing.
# Theoretically we could have a more minimal closure that does not include dependents of
# the requested generators, but this would introduce the potential for previously
# generated dependents being out of sync.
def minimal_closure(
    requested_generators: list[GeneratorKey],
    generators: dict[GeneratorKey, Generator],
) -> list[Generator]:
    closure = set(requested_generators)
    final_closure = missing_dependency_closure(closure, generators)
    # add requested generators if not already exist
    for gen_key in closure:
        if not generators[gen_key].exists:
            final_closure.add(gen_key)
    # add dependents of final_closure
    final_closure = add_dependents(final_closure, generators)
    return toposort_closure(final_closure, generators)
