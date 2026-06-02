"""Structural diff of NixOS/clan options JSON files.

Compares two options.json files (as produced by nixosOptionsDoc) and
reports added, removed, and type-changed options.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


class ChangeKind(Enum):
    ADDED = auto()
    REMOVED = auto()
    TYPE_CHANGED = auto()


@dataclass(frozen=True, slots=True)
class OptionDiff:
    """One option that differs between the two sets."""

    name: str
    kind: ChangeKind
    old_type: str | None = None
    new_type: str | None = None


@dataclass(frozen=True, slots=True)
class DiffResult:
    """Complete diff between two option sets."""

    old_label: str
    new_label: str
    added: tuple[OptionDiff, ...] = ()
    removed: tuple[OptionDiff, ...] = ()
    type_changed: tuple[OptionDiff, ...] = ()

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.type_changed)


OptionsDict = dict[str, dict[str, Any]]


def load_options(path: Path) -> OptionsDict:
    """Load an options.json file into a dict keyed by option name."""
    with path.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object, got {type(data).__name__}"
        raise TypeError(msg)
    return data


def diff_options(
    old: OptionsDict,
    new: OptionsDict,
    *,
    old_label: str = "old",
    new_label: str = "new",
) -> DiffResult:
    """Compute structural diff between two option dictionaries."""
    old_keys = {k for k in old if not k.startswith("_")}
    new_keys = {k for k in new if not k.startswith("_")}

    added = tuple(
        OptionDiff(name=k, kind=ChangeKind.ADDED) for k in sorted(new_keys - old_keys)
    )
    removed = tuple(
        OptionDiff(name=k, kind=ChangeKind.REMOVED) for k in sorted(old_keys - new_keys)
    )

    type_changed: list[OptionDiff] = []
    for k in sorted(old_keys & new_keys):
        old_type = old[k].get("type")
        new_type = new[k].get("type")
        if old_type != new_type:
            type_changed.append(
                OptionDiff(
                    name=k,
                    kind=ChangeKind.TYPE_CHANGED,
                    old_type=old_type,
                    new_type=new_type,
                )
            )

    return DiffResult(
        old_label=old_label,
        new_label=new_label,
        added=added,
        removed=removed,
        type_changed=tuple(type_changed),
    )


def format_diff(result: DiffResult, *, noun: str = "Options") -> str:
    """Render a DiffResult as a human-readable report."""
    if not result.has_changes:
        return f"No {noun.lower()} changes between {result.old_label} and {result.new_label}.\n"

    lines: list[str] = [
        f"{noun} diff: {result.old_label} -> {result.new_label}",
        f"Summary: +{len(result.added)} -{len(result.removed)} ~{len(result.type_changed)}",
        "",
    ]

    if result.added:
        lines.append(f"Added ({len(result.added)})")
        lines.extend(f"  {d.name}" for d in result.added)
        lines.append("")

    if result.removed:
        lines.append(f"Removed ({len(result.removed)})")
        lines.extend(f"  {d.name}" for d in result.removed)
        lines.append("")

    if result.type_changed:
        lines.append(f"Type changed ({len(result.type_changed)})")
        lines.extend(
            f"  {d.name}: {d.old_type} -> {d.new_type}" for d in result.type_changed
        )
        lines.append("")

    return "\n".join(lines)
