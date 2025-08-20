from clan_lib.errors import ClanError
from clan_lib.flake import Flake


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def _suggest_similar_names(
    target: str,
    candidates: list[str],
    max_suggestions: int = 3,
) -> list[str]:
    if not candidates:
        return []

    distances = [
        (candidate, _levenshtein_distance(target.lower(), candidate.lower()))
        for candidate in candidates
    ]

    distances.sort(key=lambda x: (x[1], x[0]))

    return [candidate for candidate, _ in distances[:max_suggestions]]


def get_available_machines(flake: Flake) -> list[str]:
    from clan_lib.machines.list import list_machines

    machines = list_machines(flake)
    return list(machines.keys())


def validate_machine_names(machine_names: list[str], flake: Flake) -> list[str]:
    """Returns a list of valid machine names
    that are guaranteed to exist in the referenced clan
    """
    if not machine_names:
        return []

    available_machines = get_available_machines(flake)
    invalid_machines = [
        name for name in machine_names if name not in available_machines
    ]

    if invalid_machines:
        error_lines = []
        for machine_name in invalid_machines:
            suggestions = _suggest_similar_names(machine_name, available_machines)
            if suggestions:
                suggestion_text = f"Did you mean: {', '.join(suggestions)}?"
            else:
                suggestion_text = (
                    f"Available machines: {', '.join(sorted(available_machines))}"
                )
            error_lines.append(f"Machine '{machine_name}' not found. {suggestion_text}")

        raise ClanError("\n".join(error_lines))

    return machine_names
