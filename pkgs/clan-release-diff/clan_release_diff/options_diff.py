"""Structural diff of NixOS/clan options JSON files.

Compares two options.json files (as produced by nixosOptionsDoc) and
reports added, removed, and type-changed options.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any


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


@dataclass(frozen=True, slots=True)
class ExportChange:
    """A service whose projected export interfaces differ between versions."""

    service: str
    added: tuple[str, ...]
    removed: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExportDiff:
    """Diff of per-service ``manifest.exports.out`` between two versions."""

    old_label: str
    new_label: str
    changes: tuple[ExportChange, ...] = ()

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)


@dataclass(frozen=True, slots=True)
class TemplateInfo:
    """A single template's metadata: human description and content root."""

    description: str
    path: Path


@dataclass(frozen=True, slots=True)
class DescriptionChange:
    """A template whose description text differs between versions."""

    template: str
    old: str
    new: str


@dataclass(frozen=True, slots=True)
class TemplateContentChange:
    """Files that differ inside a template present in both versions."""

    template: str
    added_files: tuple[str, ...]
    removed_files: tuple[str, ...]
    modified_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TemplateDiff:
    """Diff of ``clan.templates`` between two versions."""

    old_label: str
    new_label: str
    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    description_changed: tuple[DescriptionChange, ...] = ()
    content_changed: tuple[TemplateContentChange, ...] = ()

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added
            or self.removed
            or self.description_changed
            or self.content_changed
        )


OptionsDict = dict[str, dict[str, Any]]
ServicesDict = dict[str, set[str]]
ExportsDict = dict[str, set[str]]
TemplatesDict = dict[str, TemplateInfo]


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


def load_service_exports(path: Path) -> ExportsDict:
    """Load each service's projected export interfaces from a services info.json.

    Reads ``manifest.exports.out`` per service -- the list of export interfaces a
    service projects into the global ``exports.<name>.*`` namespace. The
    ``exports`` key is absent on releases predating the feature (e.g. 25.11), where
    the manifest only carried ``name``/``description``/``categories``/``features``;
    such services map to an empty set. Treating absence as empty means the whole
    current export surface reads as *added* against an old ref rather than raising,
    and a later removal reads as *removed* -- which is exactly the breaking signal.
    """
    with path.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object, got {type(data).__name__}"
        raise TypeError(msg)

    exports: ExportsDict = {}
    for service, entry in data.items():
        if not isinstance(entry, dict):
            continue
        manifest = entry.get("manifest", {})
        manifest_exports = (
            manifest.get("exports", {}) if isinstance(manifest, dict) else {}
        )
        out = (
            manifest_exports.get("out", [])
            if isinstance(manifest_exports, dict)
            else []
        )
        exports[service] = set(out) if isinstance(out, list) else set()
    return exports


def load_service_settings(path: Path) -> OptionsDict:
    """Load per-role settings options from a services info.json.

    Returns a flat options dict keyed by ``service/role/setting``, ready for
    :func:`diff_options`. Each role entry in info.json points to a
    nixosOptionsDoc output directory holding ``share/doc/nixos/options.json``,
    which describes that role's ``settings.*`` interface.
    """
    with path.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object, got {type(data).__name__}"
        raise TypeError(msg)

    settings: OptionsDict = {}
    for service, entry in data.items():
        if not isinstance(entry, dict):
            continue
        roles = entry.get("roles", {})
        if not isinstance(roles, dict):
            continue
        for role, role_path in roles.items():
            if not isinstance(role_path, str):
                continue
            for setting, option in _load_role_options(Path(role_path)).items():
                settings[f"{service}/{role}/{setting}"] = option
    return settings


def _load_role_options(role_dir: Path) -> OptionsDict:
    """Load one role's settings schema from its nixosOptionsDoc output dir."""
    options_json = role_dir / "share/doc/nixos/options.json"
    with options_json.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object in {options_json}, got {type(data).__name__}"
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


def diff_exports(
    old: ExportsDict,
    new: ExportsDict,
    *,
    old_label: str = "old",
    new_label: str = "new",
) -> ExportDiff:
    """Diff per-service export interfaces, restricted to shared services.

    Added/removed services are already reported by the Services layer, so only
    services present in both versions are inspected here. This attributes an
    export gain/loss to the owning service -- the missing attribution noted for
    the exports surface, where removals previously only surfaced as anonymous
    ``exports.<name>.*`` option churn in the clan layer.
    """
    changes: list[ExportChange] = []
    for service in sorted(set(old) & set(new)):
        old_exports = old[service]
        new_exports = new[service]
        if old_exports != new_exports:
            changes.append(
                ExportChange(
                    service=service,
                    added=tuple(sorted(new_exports - old_exports)),
                    removed=tuple(sorted(old_exports - new_exports)),
                )
            )
    return ExportDiff(
        old_label=old_label,
        new_label=new_label,
        changes=tuple(changes),
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


def format_export_diff(result: ExportDiff) -> str:
    """Render an ExportDiff as a human-readable report."""
    if not result.has_changes:
        return f"No export changes between {result.old_label} and {result.new_label}.\n"

    lines: list[str] = [
        f"Exports diff: {result.old_label} -> {result.new_label}",
        f"Summary: {len(result.changes)} service(s) changed",
        "",
        f"Export changes ({len(result.changes)})",
    ]
    for ch in result.changes:
        parts: list[str] = []
        parts.extend(f"+{e}" for e in ch.added)
        parts.extend(f"-{e}" for e in ch.removed)
        lines.append(f"  {ch.service}: {', '.join(parts)}")
    lines.append("")

    return "\n".join(lines)


def load_templates(path: Path) -> TemplatesDict:
    """Load a templates manifest, return {``category/name``: TemplateInfo}.

    The manifest is the JSON form of the flake's ``clan.templates`` output:
    ``{category: {name: {description, path}}}``. Each ``path`` is a directory
    holding the template's files. Keys are flattened to ``category/name`` so a
    template is identified independently of its category.
    """
    with path.open() as f:
        data: Any = json.load(f)
    if not isinstance(data, dict):
        msg = f"Expected top-level JSON object, got {type(data).__name__}"
        raise TypeError(msg)

    templates: TemplatesDict = {}
    for category, entries in data.items():
        if not isinstance(entries, dict):
            continue
        for name, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            template_path = entry.get("path")
            if not isinstance(template_path, str):
                continue
            description = entry.get("description", "")
            templates[f"{category}/{name}"] = TemplateInfo(
                description=description if isinstance(description, str) else "",
                path=Path(template_path),
            )
    return templates


def _hash_template_dir(root: Path) -> dict[str, str]:
    """Map each regular file under *root* to the sha256 of its bytes.

    Keys are POSIX paths relative to *root* so two templates can be compared
    regardless of the absolute store path each version was realised under.
    Non-regular files (symlinks, fifos) are skipped.
    """
    hashes: dict[str, str] = {}
    for file in sorted(root.rglob("*")):
        if file.is_symlink() or not file.is_file():
            continue
        rel = file.relative_to(root).as_posix()
        hashes[rel] = hashlib.sha256(file.read_bytes()).hexdigest()
    return hashes


def diff_templates(
    old: TemplatesDict,
    new: TemplatesDict,
    *,
    old_label: str = "old",
    new_label: str = "new",
) -> TemplateDiff:
    """Compute structural and content diff between two template sets."""
    old_keys = set(old)
    new_keys = set(new)

    added = tuple(sorted(new_keys - old_keys))
    removed = tuple(sorted(old_keys - new_keys))

    description_changed: list[DescriptionChange] = []
    content_changed: list[TemplateContentChange] = []
    for name in sorted(old_keys & new_keys):
        old_info = old[name]
        new_info = new[name]

        if old_info.description != new_info.description:
            description_changed.append(
                DescriptionChange(
                    template=name,
                    old=old_info.description,
                    new=new_info.description,
                )
            )

        old_hashes = _hash_template_dir(old_info.path)
        new_hashes = _hash_template_dir(new_info.path)
        old_files = set(old_hashes)
        new_files = set(new_hashes)
        added_files = tuple(sorted(new_files - old_files))
        removed_files = tuple(sorted(old_files - new_files))
        modified_files = tuple(
            f for f in sorted(old_files & new_files) if old_hashes[f] != new_hashes[f]
        )
        if added_files or removed_files or modified_files:
            content_changed.append(
                TemplateContentChange(
                    template=name,
                    added_files=added_files,
                    removed_files=removed_files,
                    modified_files=modified_files,
                )
            )

    return TemplateDiff(
        old_label=old_label,
        new_label=new_label,
        added=added,
        removed=removed,
        description_changed=tuple(description_changed),
        content_changed=tuple(content_changed),
    )


def format_template_diff(result: TemplateDiff) -> str:
    """Render a TemplateDiff as a human-readable report."""
    if not result.has_changes:
        return (
            f"No template changes between {result.old_label} and {result.new_label}.\n"
        )

    lines: list[str] = [
        f"Templates diff: {result.old_label} -> {result.new_label}",
        (
            f"Summary: +{len(result.added)} -{len(result.removed)} "
            f"desc~{len(result.description_changed)} "
            f"content~{len(result.content_changed)}"
        ),
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

    if result.description_changed:
        lines.append(f"Description changed ({len(result.description_changed)})")
        lines.extend(
            f"  {dc.template}: {dc.old} -> {dc.new}"
            for dc in result.description_changed
        )
        lines.append("")

    if result.content_changed:
        lines.append(f"Content changed ({len(result.content_changed)})")
        for cc in result.content_changed:
            lines.append(f"  {cc.template}:")
            lines.extend(f"    +{f}" for f in cc.added_files)
            lines.extend(f"    ~{f}" for f in cc.modified_files)
            lines.extend(f"    -{f}" for f in cc.removed_files)
        lines.append("")

    return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class LayerPaths:
    """Paths to the options JSON files for one version."""

    label: str
    clan_options: Path | None = None
    nixos_options: Path | None = None
    services_json: Path | None = None
    templates_json: Path | None = None


@dataclass(frozen=True, slots=True)
class MultiLayerDiff:
    """Diffs for all option layers between two versions."""

    clan: DiffResult | None = None
    nixos: DiffResult | None = None
    services: ServiceDiff | None = None
    service_settings: DiffResult | None = None
    exports: ExportDiff | None = None
    templates: TemplateDiff | None = None


def _service_role(key: str) -> str:
    """Return the ``service/role`` prefix of a ``service/role/setting`` key."""
    service, role, _setting = key.split("/", 2)
    return f"{service}/{role}"


def _shared_role_settings(
    old: OptionsDict, new: OptionsDict
) -> tuple[OptionsDict, OptionsDict]:
    """Restrict two settings dicts to service/role pairs present in both.

    Settings of a service or role that exists on only one side are dropped:
    the services layer already reports those as added/removed services or
    roles, so re-listing their settings would be redundant noise.
    """
    shared = {_service_role(k) for k in old} & {_service_role(k) for k in new}
    old_kept = {k: v for k, v in old.items() if _service_role(k) in shared}
    new_kept = {k: v for k, v in new.items() if _service_role(k) in shared}
    return old_kept, new_kept


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
    settings_diff = None
    exports_diff = None
    if old.services_json and new.services_json:
        services_diff = diff_services(
            load_services(old.services_json),
            load_services(new.services_json),
            old_label=old.label,
            new_label=new.label,
        )
        old_settings, new_settings = _shared_role_settings(
            load_service_settings(old.services_json),
            load_service_settings(new.services_json),
        )
        settings_diff = diff_options(
            old_settings,
            new_settings,
            old_label=old.label,
            new_label=new.label,
        )
        exports_diff = diff_exports(
            load_service_exports(old.services_json),
            load_service_exports(new.services_json),
            old_label=old.label,
            new_label=new.label,
        )

    templates_diff = None
    if old.templates_json and new.templates_json:
        templates_diff = diff_templates(
            load_templates(old.templates_json),
            load_templates(new.templates_json),
            old_label=old.label,
            new_label=new.label,
        )

    return MultiLayerDiff(
        clan=clan_diff,
        nixos=nixos_diff,
        services=services_diff,
        service_settings=settings_diff,
        exports=exports_diff,
        templates=templates_diff,
    )


def _validate_layer_pairs(old: LayerPaths, new: LayerPaths) -> None:
    for name, old_path, new_path in (
        ("clan", old.clan_options, new.clan_options),
        ("nixos", old.nixos_options, new.nixos_options),
        ("services", old.services_json, new.services_json),
        ("templates", old.templates_json, new.templates_json),
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

    if diff.exports is not None:
        parts.append("## Service exports")
        parts.append("")
        parts.append(format_export_diff(diff.exports))

    if diff.service_settings is not None:
        parts.append("## Service settings")
        parts.append("")
        parts.append(format_diff(diff.service_settings, noun="Service settings"))

    if diff.templates is not None:
        parts.append("## Templates")
        parts.append("")
        parts.append(format_template_diff(diff.templates))

    if not parts:
        return "No option layers provided.\n"

    return "\n".join(parts)
