from __future__ import annotations

from graphlib import TopologicalSorter
from typing import TYPE_CHECKING

from clan_lib.errors import ClanError
from clan_lib.vars.generator import Comparable

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .generator import Comparable, Generator


class GeneratorNotFoundError(ClanError):
    pass


def missing_dependency_closure[T: Comparable](
    requested_generators: Iterable[T],
    generators: dict[T, Generator],
) -> set[T]:
    closure = set(requested_generators)
    # extend the graph to include all dependencies which are not on disk
    dep_closure: set[T] = set()
    queue = list(closure)
    while queue:
        gen_key = queue.pop(0)

        if gen_key not in generators:
            msg = f"Requested generator {gen_key} not found"
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


def add_missing_dependencies[T: Comparable](
    requested_generators: Iterable[T],
    generators: dict[T, Generator],
) -> set[T]:
    closure = set(requested_generators)
    return missing_dependency_closure(closure, generators) | closure


def add_dependents[T: Comparable](
    requested_generators: Iterable[T],
    generators: dict[T, Generator],
) -> set[T]:
    closure = set(requested_generators)
    # build reverse dependency graph (graph of dependents)
    dependents_graph: dict[Comparable, set[Comparable]] = {}
    for gen_key, gen in generators.items():
        for dep_key in gen.dependencies:
            if dep_key not in dependents_graph:
                dependents_graph[dep_key] = set()
            dependents_graph[dep_key].add(gen_key)
    # extend the graph to include all dependents of the current closure
    queue = list(closure)
    while queue:
        gen_key = queue.pop(0)
        for dep_key_comp in dependents_graph.get(gen_key, []):
            if dep_key_comp not in closure:
                closure.add(dep_key_comp)
                queue.append(dep_key_comp)
    return closure


def toposort_closure[T: Comparable](
    _closure: Iterable[T],
    generators: dict[T, Generator],
) -> list[Generator]:
    closure = set(_closure)
    # return the topological sorted list of generators to execute
    final_dep_graph = {}
    for gen_key in sorted(closure, key=lambda k: k.key()):
        deps = set(generators[gen_key].dependencies) & closure
        final_dep_graph[gen_key] = deps
    sorter = TopologicalSorter(final_dep_graph)
    result = list(sorter.static_order())
    return [generators[gen_key] for gen_key in result]


# just the missing generators including their dependents
def all_missing_closure[T: Comparable](
    requested_generators: Iterable[T],
    generators: dict[T, Generator],
) -> list[Generator]:
    """From a set of generators, return all incomplete generators in topological order.

    incomplete
    : A generator is missing if at least one of its files is missing.
    """
    # collect all generators that are missing from disk
    closure: set[T] = {
        gen_key for gen_key in requested_generators if not generators[gen_key].exists
    }
    closure = add_dependents(closure, generators)
    return toposort_closure(closure, generators)


# only a selected list of generators including their missing dependencies and their dependents
def requested_closure[T: Comparable](
    requested_generators: Iterable[T],
    generators: dict[T, Generator],
) -> list[Generator]:
    closure = set(requested_generators)
    # extend the graph to include all dependencies which are not on disk
    closure = add_missing_dependencies(closure, generators)
    closure = add_dependents(closure, generators)
    return toposort_closure(closure, generators)
