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


@dataclass(frozen=True, slots=True)
class RoleChange:
    """A service whose roles differ between the two versions."""

    service: str
    added_roles: tuple[str, ...]
    removed_roles: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ServiceDiff:
    """Complete diff between two service sets."""

    old_label: str
    new_label: str
    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    role_changes: tuple[RoleChange, ...] = ()

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.role_changes)


OptionsDict = dict[str, dict[str, Any]]
ServicesDict = dict[str, set[str]]


def load_options(path: Path) -> OptionsDict:
    """Load an options.json file into a dict keyed by option name."""
    with path.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object, got {type(data).__name__}"
        raise TypeError(msg)
    return data


def load_services(path: Path) -> ServicesDict:
    """Load a services JSON file, return {service_name: {role_names}}."""
    with path.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object, got {type(data).__name__}"
        raise TypeError(msg)
    return {
        name: set(entry.get("roles", {}).keys()) if isinstance(entry, dict) else set()
        for name, entry in data.items()
    }


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


def diff_services(
    old: ServicesDict,
    new: ServicesDict,
    *,
    old_label: str = "old",
    new_label: str = "new",
) -> ServiceDiff:
    """Compute structural diff between two service dictionaries."""
    old_names = set(old)
    new_names = set(new)

    added = tuple(sorted(new_names - old_names))
    removed = tuple(sorted(old_names - new_names))

    role_changes: list[RoleChange] = []
    for name in sorted(old_names & new_names):
        old_roles = old[name]
        new_roles = new[name]
        if old_roles != new_roles:
            role_changes.append(
                RoleChange(
                    service=name,
                    added_roles=tuple(sorted(new_roles - old_roles)),
                    removed_roles=tuple(sorted(old_roles - new_roles)),
                )
            )

    return ServiceDiff(
        old_label=old_label,
        new_label=new_label,
        added=added,
        removed=removed,
        role_changes=tuple(role_changes),
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


def format_service_diff(result: ServiceDiff) -> str:
    """Render a ServiceDiff as a human-readable report."""
    if not result.has_changes:
        return (
            f"No service changes between {result.old_label} and {result.new_label}.\n"
        )

    lines: list[str] = [
        f"Services diff: {result.old_label} -> {result.new_label}",
        f"Summary: +{len(result.added)} -{len(result.removed)} roles~{len(result.role_changes)}",
        "",
    ]

    if result.added:
        lines.append(f"Added ({len(result.added)})")
        lines.extend(f"  {name}" for name in result.added)
        lines.append("")

    if result.removed:
        lines.append(f"Removed ({len(result.removed)})")
        lines.extend(f"  {name}" for name in result.removed)
        lines.append("")

    if result.role_changes:
        lines.append(f"Role changes ({len(result.role_changes)})")
        for rc in result.role_changes:
            parts: list[str] = []
            parts.extend(f"+{r}" for r in rc.added_roles)
            parts.extend(f"-{r}" for r in rc.removed_roles)
            lines.append(f"  {rc.service}: {', '.join(parts)}")
        lines.append("")

    return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class LayerPaths:
    """Paths to the options JSON files for one version."""

    label: str
    clan_options: Path | None = None
    nixos_options: Path | None = None
    services_json: Path | None = None


@dataclass(frozen=True, slots=True)
class MultiLayerDiff:
    """Diffs for all option layers between two versions."""

    clan: DiffResult | None = None
    nixos: DiffResult | None = None
    services: ServiceDiff | None = None


def diff_layers(old: LayerPaths, new: LayerPaths) -> MultiLayerDiff:
    """Diff all available option layers between two versions."""
    _validate_layer_pairs(old, new)

    clan_diff = None
    if old.clan_options and new.clan_options:
        clan_diff = diff_options(
            load_options(old.clan_options),
            load_options(new.clan_options),
            old_label=old.label,
            new_label=new.label,
        )

    nixos_diff = None
    if old.nixos_options and new.nixos_options:
        nixos_diff = diff_options(
            load_options(old.nixos_options),
            load_options(new.nixos_options),
            old_label=old.label,
            new_label=new.label,
        )

    services_diff = None
    if old.services_json and new.services_json:
        services_diff = diff_services(
            load_services(old.services_json),
            load_services(new.services_json),
            old_label=old.label,
            new_label=new.label,
        )

    return MultiLayerDiff(
        clan=clan_diff,
        nixos=nixos_diff,
        services=services_diff,
    )


def _validate_layer_pairs(old: LayerPaths, new: LayerPaths) -> None:
    for name, old_path, new_path in (
        ("clan", old.clan_options, new.clan_options),
        ("nixos", old.nixos_options, new.nixos_options),
        ("services", old.services_json, new.services_json),
    ):
        if bool(old_path) != bool(new_path):
            provided = "old" if old_path else "new"
            missing = "new" if old_path else "old"
            msg = f"Layer '{name}': {provided} path provided but {missing} path missing"
            raise ValueError(msg)


def format_multi_layer_diff(diff: MultiLayerDiff) -> str:
    """Render all layers into a single report."""
    parts: list[str] = []

    for layer_name, result in (
        ("Clan (flake) options", diff.clan),
        ("NixOS (clan.core.*) options", diff.nixos),
    ):
        if result is None:
            continue
        parts.append(f"## {layer_name}")
        parts.append("")
        parts.append(format_diff(result))

    if diff.services is not None:
        parts.append("## Services")
        parts.append("")
        parts.append(format_service_diff(diff.services))

    if not parts:
        return "No option layers provided.\n"

    return "\n".join(parts)
