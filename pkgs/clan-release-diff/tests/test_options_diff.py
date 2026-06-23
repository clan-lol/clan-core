"""Tests for clan_release_diff.options_diff."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

import pytest
from clan_release_diff.options_diff import (
    ChangeKind,
    DescriptionChange,
    DiffResult,
    ExportChange,
    ExportDiff,
    LayerPaths,
    MultiLayerDiff,
    OptionDiff,
    RoleChange,
    ServiceDiff,
    TemplateContentChange,
    TemplateDiff,
    TemplateInfo,
    diff_exports,
    diff_layers,
    diff_options,
    diff_services,
    diff_templates,
    format_diff,
    format_export_diff,
    format_multi_layer_diff,
    format_service_diff,
    format_template_diff,
    load_options,
    load_service_exports,
    load_service_settings,
    load_services,
    load_templates,
)

OPTION_A: dict[str, Any] = {
    "type": "string",
    "default": {"_type": "literalExpression", "text": '"hello"'},
    "description": "A greeting",
    "declarations": ["/nix/store/xxx/modules/foo.nix"],
}

OPTION_B: dict[str, Any] = {
    "type": "integer",
    "default": {"_type": "literalExpression", "text": "42"},
    "description": "The answer",
    "declarations": ["/nix/store/yyy/modules/bar.nix"],
}

SERVICE_BORGBACKUP: dict[str, Any] = {
    "manifest": {"name": "borgbackup", "description": "Backup service"},
    "roles": {"client": {}, "server": {}},
}

SERVICE_WIREGUARD: dict[str, Any] = {
    "manifest": {"name": "wireguard", "description": "VPN"},
    "roles": {"peer": {}},
}

SERVICE_NO_ROLES: dict[str, Any] = {
    "manifest": {"name": "simple", "description": "No roles"},
}


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    path.write_text(json.dumps(data))
    return path


def _section_items(text: str, header: str) -> list[str]:
    """Return the stripped item lines under *header* in formatted output.

    Sections start with a non-indented header line (e.g. 'Added (2)') and
    contain indented item lines.  The section ends at the next blank line or
    non-indented line.
    """
    lines = text.splitlines()
    items: list[str] = []
    in_section = False
    for line in lines:
        if not in_section:
            if line.startswith(header):
                in_section = True
            continue
        # Inside section: indented lines are items, blank/non-indented ends it
        if line and line[0] == " ":
            items.append(line.strip())
        else:
            break
    return items


def _write_role_options(base: Path, settings: dict[str, Any]) -> Path:
    """Create a nixosOptionsDoc-style dir with share/doc/nixos/options.json."""
    options_dir = base / "share" / "doc" / "nixos"
    options_dir.mkdir(parents=True, exist_ok=True)
    (options_dir / "options.json").write_text(json.dumps(settings))
    return base


def _write_services(
    base: Path,
    prefix: str,
    services: dict[str, dict[str, dict[str, Any]]],
) -> Path:
    """Write an info.json plus per-role options dirs.

    ``services`` maps service -> role -> {setting: option-entry}. Returns the
    path to info.json, with each role pointing at its generated options dir.
    """
    info: dict[str, Any] = {}
    for service, roles in services.items():
        role_map: dict[str, str] = {}
        for role, settings in roles.items():
            role_dir = _write_role_options(
                base / f"{prefix}-{service}-{role}", settings
            )
            role_map[role] = str(role_dir)
        info[service] = {"manifest": {"name": service}, "roles": role_map}
    return _write_json(base / f"{prefix}-info.json", info)


class TestLoadOptions:
    def test_loads_valid_json(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "opts.json", {"clan.foo": OPTION_A})
        result = load_options(p)
        assert "clan.foo" in result
        assert result["clan.foo"]["type"] == "string"

    def test_rejects_non_object(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "bad.json", [1, 2, 3])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="Expected top-level JSON object"):
            load_options(p)


class TestDiffOptions:
    def test_identical(self) -> None:
        opts = {"clan.foo": OPTION_A}
        result = diff_options(opts, opts, old_label="a", new_label="b")
        assert not result.has_changes
        assert result.added == ()
        assert result.removed == ()
        assert result.type_changed == ()

    def test_both_empty(self) -> None:
        result = diff_options({}, {}, old_label="a", new_label="b")
        assert not result.has_changes

    def test_added(self) -> None:
        result = diff_options({}, {"clan.foo": OPTION_A})
        assert len(result.added) == 1
        assert result.added[0].name == "clan.foo"
        assert result.added[0].kind == ChangeKind.ADDED
        assert not result.removed
        assert not result.type_changed

    def test_removed(self) -> None:
        result = diff_options({"clan.foo": OPTION_A}, {})
        assert len(result.removed) == 1
        assert result.removed[0].name == "clan.foo"
        assert result.removed[0].kind == ChangeKind.REMOVED

    def test_added_and_removed(self) -> None:
        result = diff_options({"clan.foo": OPTION_A}, {"clan.bar": OPTION_B})
        assert len(result.added) == 1
        assert result.added[0].name == "clan.bar"
        assert len(result.removed) == 1
        assert result.removed[0].name == "clan.foo"

    def test_type_changed(self) -> None:
        modified = {**OPTION_A, "type": "null or string"}
        result = diff_options({"x": OPTION_A}, {"x": modified})
        assert len(result.type_changed) == 1
        d = result.type_changed[0]
        assert d.name == "x"
        assert d.kind == ChangeKind.TYPE_CHANGED
        assert d.old_type == "string"
        assert d.new_type == "null or string"

    def test_description_change_ignored(self) -> None:
        modified = {**OPTION_A, "description": "Something else entirely"}
        result = diff_options({"x": OPTION_A}, {"x": modified})
        assert not result.has_changes

    def test_default_change_ignored(self) -> None:
        modified = {
            **OPTION_A,
            "default": {"_type": "literalExpression", "text": '"goodbye"'},
        }
        result = diff_options({"x": OPTION_A}, {"x": modified})
        assert not result.has_changes

    def test_declaration_change_ignored(self) -> None:
        modified = {**OPTION_A, "declarations": ["/nix/store/DIFFERENT/foo.nix"]}
        result = diff_options({"x": OPTION_A}, {"x": modified})
        assert not result.has_changes

    def test_internal_options_skipped(self) -> None:
        """Options starting with _ are internal and should be excluded."""
        old: dict[str, Any] = {"_module.args": OPTION_A, "visible": OPTION_A}
        new: dict[str, Any] = {"_module.args": OPTION_B, "visible": OPTION_A}
        result = diff_options(old, new)
        assert not result.has_changes  # type differs but key is internal

    def test_internal_options_not_in_added_removed(self) -> None:
        old: dict[str, Any] = {"_internal": OPTION_A}
        new: dict[str, Any] = {"_other": OPTION_B}
        result = diff_options(old, new)
        assert not result.added
        assert not result.removed

    def test_results_sorted(self) -> None:
        old = {"z": OPTION_A, "a": OPTION_B}
        new = {"m": OPTION_A, "a": OPTION_B}
        result = diff_options(old, new)
        assert result.added[0].name == "m"
        assert result.removed[0].name == "z"


class TestFormatDiff:
    def test_no_changes(self) -> None:
        result = DiffResult(old_label="25.11", new_label="main")
        text = format_diff(result)
        assert "No options changes" in text
        assert "25.11" in text
        assert "main" in text

    def test_with_changes(self) -> None:
        result = DiffResult(
            old_label="25.11",
            new_label="main",
            added=(OptionDiff(name="clan.new", kind=ChangeKind.ADDED),),
            removed=(OptionDiff(name="clan.old", kind=ChangeKind.REMOVED),),
            type_changed=(
                OptionDiff(
                    name="clan.modified",
                    kind=ChangeKind.TYPE_CHANGED,
                    old_type="string",
                    new_type="path",
                ),
            ),
        )
        text = format_diff(result)
        assert "Summary: +1 -1 ~1" in text
        assert _section_items(text, "Added") == ["clan.new"]
        assert _section_items(text, "Removed") == ["clan.old"]
        assert _section_items(text, "Type changed") == ["clan.modified: string -> path"]

    def test_summary_before_sections(self) -> None:
        result = DiffResult(
            old_label="a",
            new_label="b",
            added=(OptionDiff(name="x", kind=ChangeKind.ADDED),),
        )
        text = format_diff(result)
        assert text.index("Summary:") < text.index("Added")

    def test_noun_in_header(self) -> None:
        result = DiffResult(
            old_label="a",
            new_label="b",
            added=(OptionDiff(name="x", kind=ChangeKind.ADDED),),
        )
        text = format_diff(result, noun="Service settings")
        assert "Service settings diff: a -> b" in text

    def test_noun_in_no_changes(self) -> None:
        text = format_diff(
            DiffResult(old_label="a", new_label="b"), noun="Service settings"
        )
        assert "No service settings changes" in text


class TestLoadServices:
    def test_loads_valid_json(self, tmp_path: Path) -> None:
        p = _write_json(
            tmp_path / "services.json",
            {"borgbackup": SERVICE_BORGBACKUP, "wireguard": SERVICE_WIREGUARD},
        )
        result = load_services(p)
        assert result == {
            "borgbackup": {"client", "server"},
            "wireguard": {"peer"},
        }

    def test_no_roles_key(self, tmp_path: Path) -> None:
        """Services without a 'roles' key get an empty role set."""
        p = _write_json(tmp_path / "services.json", {"simple": SERVICE_NO_ROLES})
        result = load_services(p)
        assert result == {"simple": set()}

    def test_empty(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "services.json", {})
        result = load_services(p)
        assert result == {}

    def test_rejects_non_object(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "bad.json", [1, 2])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="Expected top-level JSON object"):
            load_services(p)


class TestLoadServiceSettings:
    def test_flat_keys_with_types(self, tmp_path: Path) -> None:
        info = _write_services(
            tmp_path,
            "v",
            {
                "zerotier": {
                    "controller": {"allowedIds": {"type": "list of string"}},
                    "peer": {"port": {"type": "port number"}},
                },
            },
        )
        result = load_service_settings(info)
        assert result["zerotier/controller/allowedIds"]["type"] == "list of string"
        assert result["zerotier/peer/port"]["type"] == "port number"

    def test_skips_non_dict_service_entry(self, tmp_path: Path) -> None:
        info = _write_json(tmp_path / "info.json", {"weird": "not-a-dict"})
        assert load_service_settings(info) == {}

    def test_skips_non_str_role_value(self, tmp_path: Path) -> None:
        info = _write_json(
            tmp_path / "info.json",
            {"svc": {"roles": {"default": 123}}},
        )
        assert load_service_settings(info) == {}

    def test_rejects_non_object(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "bad.json", [1, 2])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="Expected top-level JSON object"):
            load_service_settings(p)


class TestDiffServices:
    def test_identical(self) -> None:
        services = {"a": {"default"}, "b": {"client", "server"}}
        result = diff_services(services, services)
        assert not result.has_changes

    def test_added(self) -> None:
        old: dict[str, set[str]] = {}
        new = {"wireguard": {"peer"}, "borgbackup": {"client"}}
        result = diff_services(old, new, old_label="25.11", new_label="main")
        assert result.added == ("borgbackup", "wireguard")
        assert result.removed == ()
        assert result.role_changes == ()
        assert result.old_label == "25.11"
        assert result.new_label == "main"

    def test_removed(self) -> None:
        old = {"coredns": {"default"}, "wireguard": {"peer"}}
        new = {"wireguard": {"peer"}}
        result = diff_services(old, new)
        assert result.removed == ("coredns",)
        assert result.added == ()

    def test_role_changes(self) -> None:
        old = {"monitoring": {"telegraf"}, "data-mesher": set()}
        new = {
            "monitoring": {"client", "server"},
            "data-mesher": {"bootstrap", "default"},
        }
        result = diff_services(old, new)
        assert result.added == ()
        assert result.removed == ()
        assert len(result.role_changes) == 2
        # Sorted by service name
        dm = result.role_changes[0]
        assert dm.service == "data-mesher"
        assert dm.added_roles == ("bootstrap", "default")
        assert dm.removed_roles == ()
        mon = result.role_changes[1]
        assert mon.service == "monitoring"
        assert mon.added_roles == ("client", "server")
        assert mon.removed_roles == ("telegraf",)

    def test_mixed(self) -> None:
        """Added, removed, and role-changed services in one diff."""
        old = {"coredns": {"default"}, "borgbackup": {"client"}}
        new = {"pki": {"default"}, "borgbackup": {"client", "server"}}
        result = diff_services(old, new)
        assert result.added == ("pki",)
        assert result.removed == ("coredns",)
        assert len(result.role_changes) == 1
        assert result.role_changes[0].service == "borgbackup"
        assert result.role_changes[0].added_roles == ("server",)

    def test_no_role_change_when_identical(self) -> None:
        """Services present in both with same roles produce no RoleChange."""
        old = {"a": {"x", "y"}, "b": {"z"}}
        new = {"a": {"y", "x"}, "b": {"z"}}
        result = diff_services(old, new)
        assert not result.has_changes


class TestFormatServiceDiff:
    def test_no_changes(self) -> None:
        result = ServiceDiff(old_label="25.11", new_label="main")
        text = format_service_diff(result)
        assert "No service changes" in text
        assert "25.11" in text
        assert "main" in text

    def test_all_sections(self) -> None:
        result = ServiceDiff(
            old_label="25.11",
            new_label="main",
            added=("installer", "pki"),
            removed=("coredns",),
            role_changes=(
                RoleChange(
                    service="monitoring",
                    added_roles=("client",),
                    removed_roles=("telegraf",),
                ),
            ),
        )
        text = format_service_diff(result)

        assert "Services diff: 25.11 -> main" in text
        assert "Summary: +2 -1 roles~1" in text
        # Items appear under their correct section, in order
        assert _section_items(text, "Added") == ["installer", "pki"]
        assert _section_items(text, "Removed") == ["coredns"]
        assert _section_items(text, "Role changes") == [
            "monitoring: +client, -telegraf"
        ]

    def test_summary_before_sections(self) -> None:
        result = ServiceDiff(old_label="a", new_label="b", added=("x",))
        text = format_service_diff(result)
        assert text.index("Summary:") < text.index("Added")


class TestDiffLayers:
    def test_both_option_layers(self, tmp_path: Path) -> None:
        old_clan = _write_json(tmp_path / "old_clan.json", {"clan.a": OPTION_A})
        new_clan = _write_json(tmp_path / "new_clan.json", {})
        old_nixos = _write_json(tmp_path / "old_nixos.json", {})
        new_nixos = _write_json(tmp_path / "new_nixos.json", {"clan.core.b": OPTION_B})

        result = diff_layers(
            LayerPaths(label="25.11", clan_options=old_clan, nixos_options=old_nixos),
            LayerPaths(label="main", clan_options=new_clan, nixos_options=new_nixos),
        )

        assert result.clan is not None
        assert len(result.clan.removed) == 1
        assert result.nixos is not None
        assert len(result.nixos.added) == 1

    def test_partial_layers(self, tmp_path: Path) -> None:
        """Only clan layer provided; nixos is None."""
        old_clan = _write_json(tmp_path / "old.json", {"a": OPTION_A})
        new_clan = _write_json(tmp_path / "new.json", {"a": OPTION_A})

        result = diff_layers(
            LayerPaths(label="old", clan_options=old_clan),
            LayerPaths(label="new", clan_options=new_clan),
        )
        assert result.clan is not None
        assert not result.clan.has_changes
        assert result.nixos is None

    def test_with_services(self, tmp_path: Path) -> None:
        old_svc = _write_json(
            tmp_path / "old_svc.json",
            {"borgbackup": SERVICE_BORGBACKUP, "coredns": {"roles": {"default": {}}}},
        )
        new_svc = _write_json(
            tmp_path / "new_svc.json",
            {"borgbackup": SERVICE_BORGBACKUP, "pki": {"roles": {"default": {}}}},
        )
        result = diff_layers(
            LayerPaths(label="old", services_json=old_svc),
            LayerPaths(label="new", services_json=new_svc),
        )
        assert result.services is not None
        assert result.services.added == ("pki",)
        assert result.services.removed == ("coredns",)
        assert result.clan is None
        assert result.nixos is None

    def test_service_settings_intersection(self, tmp_path: Path) -> None:
        """Only services and roles present in both refs are diffed."""
        old = _write_services(
            tmp_path,
            "old",
            {
                "borgbackup": {
                    "server": {
                        "compression": {"type": "string"},
                        "keep": {"type": "integer"},
                    }
                },
                "coredns": {"default": {"port": {"type": "integer"}}},
            },
        )
        new = _write_services(
            tmp_path,
            "new",
            {
                "borgbackup": {"server": {"keep": {"type": "string"}}},
                "pki": {"default": {"ca": {"type": "string"}}},
            },
        )
        result = diff_layers(
            LayerPaths(label="a", services_json=old),
            LayerPaths(label="b", services_json=new),
        )
        ss = result.service_settings
        assert ss is not None
        # borgbackup/server shared; coredns (removed) and pki (added) excluded
        assert [d.name for d in ss.removed] == ["borgbackup/server/compression"]
        assert [d.name for d in ss.type_changed] == ["borgbackup/server/keep"]
        assert ss.added == ()
        joined = " ".join(d.name for d in (*ss.added, *ss.removed, *ss.type_changed))
        assert "coredns" not in joined
        assert "pki" not in joined

    def test_service_settings_added_setting(self, tmp_path: Path) -> None:
        old = _write_services(
            tmp_path, "old", {"svc": {"server": {"a": {"type": "integer"}}}}
        )
        new = _write_services(
            tmp_path,
            "new",
            {"svc": {"server": {"a": {"type": "integer"}, "b": {"type": "integer"}}}},
        )
        result = diff_layers(
            LayerPaths(label="a", services_json=old),
            LayerPaths(label="b", services_json=new),
        )
        assert result.service_settings is not None
        assert [d.name for d in result.service_settings.added] == ["svc/server/b"]

    def test_service_settings_excludes_added_role(self, tmp_path: Path) -> None:
        """A role added to a shared service is not double-reported here."""
        old = _write_services(
            tmp_path, "old", {"svc": {"server": {"a": {"type": "integer"}}}}
        )
        new = _write_services(
            tmp_path,
            "new",
            {
                "svc": {
                    "server": {"a": {"type": "integer"}},
                    "client": {"b": {"type": "integer"}},
                }
            },
        )
        result = diff_layers(
            LayerPaths(label="a", services_json=old),
            LayerPaths(label="b", services_json=new),
        )
        assert result.service_settings is not None
        # server/a unchanged; client/b is an added role -> excluded
        assert not result.service_settings.has_changes

    def test_rejects_asymmetric_clan(self, tmp_path: Path) -> None:
        old_clan = _write_json(tmp_path / "old.json", {})
        with pytest.raises(ValueError, match=r"clan.*old.*provided.*new.*missing"):
            diff_layers(
                LayerPaths(label="old", clan_options=old_clan),
                LayerPaths(label="new"),
            )

    def test_rejects_asymmetric_nixos(self, tmp_path: Path) -> None:
        new_nixos = _write_json(tmp_path / "new.json", {})
        with pytest.raises(ValueError, match=r"nixos.*new.*provided.*old.*missing"):
            diff_layers(
                LayerPaths(label="old"),
                LayerPaths(label="new", nixos_options=new_nixos),
            )

    def test_rejects_asymmetric_services(self, tmp_path: Path) -> None:
        old_svc = _write_json(tmp_path / "old.json", {})
        with pytest.raises(ValueError, match=r"services.*old.*provided.*new.*missing"):
            diff_layers(
                LayerPaths(label="old", services_json=old_svc),
                LayerPaths(label="new"),
            )


class TestFormatMultiLayerDiff:
    def test_empty(self) -> None:
        text = format_multi_layer_diff(MultiLayerDiff())
        assert "No option layers provided" in text

    def test_with_clan_data(self) -> None:
        clan_result = DiffResult(
            old_label="25.11",
            new_label="main",
            added=(OptionDiff(name="clan.new", kind=ChangeKind.ADDED),),
        )
        text = format_multi_layer_diff(MultiLayerDiff(clan=clan_result))
        assert "## Clan (flake) options" in text
        assert "clan.new" in text

    def test_with_services(self) -> None:
        svc_result = ServiceDiff(
            old_label="25.11",
            new_label="main",
            added=("pki",),
        )
        text = format_multi_layer_diff(MultiLayerDiff(services=svc_result))
        assert "## Services" in text
        assert "pki" in text

    def test_all_layers_ordered(self) -> None:
        clan_result = DiffResult(
            old_label="25.11",
            new_label="main",
            added=(OptionDiff(name="clan.new", kind=ChangeKind.ADDED),),
        )
        svc_result = ServiceDiff(
            old_label="25.11",
            new_label="main",
            removed=("coredns",),
        )
        text = format_multi_layer_diff(
            MultiLayerDiff(clan=clan_result, services=svc_result)
        )
        assert "## Clan (flake) options" in text
        assert "## Services" in text
        # Services section comes after clan section
        assert text.index("## Clan") < text.index("## Services")

    def test_with_service_settings(self) -> None:
        ss = DiffResult(
            old_label="25.11",
            new_label="main",
            removed=(
                OptionDiff(
                    name="zerotier/controller/allowedIds",
                    kind=ChangeKind.REMOVED,
                ),
            ),
        )
        text = format_multi_layer_diff(MultiLayerDiff(service_settings=ss))
        assert "## Service settings" in text
        assert "Service settings diff: 25.11 -> main" in text
        assert _section_items(text, "Removed") == ["zerotier/controller/allowedIds"]

    def test_services_before_service_settings(self) -> None:
        svc = ServiceDiff(old_label="a", new_label="b", added=("pki",))
        ss = DiffResult(
            old_label="a",
            new_label="b",
            removed=(OptionDiff(name="pki/default/foo", kind=ChangeKind.REMOVED),),
        )
        text = format_multi_layer_diff(
            MultiLayerDiff(services=svc, service_settings=ss)
        )
        assert text.index("## Services") < text.index("## Service settings")


def _svc_entry(
    *,
    exports_out: list[str] | None = None,
    has_manifest: bool = True,
) -> dict[str, Any]:
    """Build an info.json service entry, optionally with manifest exports."""
    entry: dict[str, Any] = {"roles": {"default": {}}}
    if has_manifest:
        manifest: dict[str, Any] = {"name": "svc"}
        if exports_out is not None:
            manifest["exports"] = {"out": exports_out, "inputs": []}
        entry["manifest"] = manifest
    return entry


class TestLoadServiceExports:
    def test_reads_exports_out(self, tmp_path: Path) -> None:
        info = _write_json(
            tmp_path / "info.json",
            {"zerotier": _svc_entry(exports_out=["networking", "peer"])},
        )
        assert load_service_exports(info) == {"zerotier": {"networking", "peer"}}

    def test_missing_exports_key_is_empty(self, tmp_path: Path) -> None:
        """A manifest predating the exports feature (e.g. 25.11) yields empty set."""
        info = _write_json(
            tmp_path / "info.json",
            {"borgbackup": _svc_entry()},
        )
        assert load_service_exports(info) == {"borgbackup": set()}

    def test_missing_manifest_is_empty(self, tmp_path: Path) -> None:
        info = _write_json(
            tmp_path / "info.json",
            {"svc": _svc_entry(has_manifest=False)},
        )
        assert load_service_exports(info) == {"svc": set()}

    def test_skips_non_dict_entry(self, tmp_path: Path) -> None:
        info = _write_json(tmp_path / "info.json", {"weird": "not-a-dict"})
        assert load_service_exports(info) == {}

    def test_non_list_out_is_empty(self, tmp_path: Path) -> None:
        info = _write_json(
            tmp_path / "info.json",
            {"svc": {"manifest": {"exports": {"out": "oops"}}}},
        )
        assert load_service_exports(info) == {"svc": set()}

    def test_rejects_non_object(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "bad.json", [1, 2])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="Expected top-level JSON object"):
            load_service_exports(p)


class TestDiffExports:
    def test_identical(self) -> None:
        exports = {"zerotier": {"networking", "peer"}}
        result = diff_exports(exports, exports)
        assert not result.has_changes

    def test_added_export(self) -> None:
        old = {"zerotier": {"networking"}}
        new = {"zerotier": {"networking", "peer"}}
        result = diff_exports(old, new, old_label="25.11", new_label="main")
        assert len(result.changes) == 1
        ch = result.changes[0]
        assert ch.service == "zerotier"
        assert ch.added == ("peer",)
        assert ch.removed == ()

    def test_removed_export(self) -> None:
        old = {"zerotier": {"networking", "peer"}}
        new = {"zerotier": {"networking"}}
        result = diff_exports(old, new)
        ch = result.changes[0]
        assert ch.removed == ("peer",)
        assert ch.added == ()

    def test_whole_surface_added_against_old_ref(self) -> None:
        """25.11 has no exports; current ones all read as added, not as errors."""
        old: dict[str, set[str]] = {"zerotier": set(), "borgbackup": set()}
        new = {"zerotier": {"networking", "peer"}, "borgbackup": set()}
        result = diff_exports(old, new)
        assert len(result.changes) == 1
        assert result.changes[0].service == "zerotier"
        assert result.changes[0].added == ("networking", "peer")

    def test_restricted_to_shared_services(self) -> None:
        """Exports of added/removed services are left to the Services layer."""
        old = {"gone": {"x"}}
        new = {"fresh": {"y"}}
        result = diff_exports(old, new)
        assert not result.has_changes

    def test_changes_sorted_by_service(self) -> None:
        old = {"b": {"x"}, "a": {"y"}}
        new: dict[str, set[str]] = {"b": set(), "a": set()}
        result = diff_exports(old, new)
        assert [c.service for c in result.changes] == ["a", "b"]


class TestFormatExportDiff:
    def test_no_changes(self) -> None:
        text = format_export_diff(ExportDiff(old_label="25.11", new_label="main"))
        assert "No export changes" in text
        assert "25.11" in text

    def test_with_changes(self) -> None:
        result = ExportDiff(
            old_label="25.11",
            new_label="main",
            changes=(
                ExportChange(
                    service="zerotier",
                    added=("peer",),
                    removed=("networking",),
                ),
            ),
        )
        text = format_export_diff(result)
        assert "Exports diff: 25.11 -> main" in text
        assert "Summary: 1 service(s) changed" in text
        assert _section_items(text, "Export changes") == [
            "zerotier: +peer, -networking"
        ]


class TestDiffLayersExports:
    def test_exports_attributed_to_service(self, tmp_path: Path) -> None:
        old = _write_json(
            tmp_path / "old.json",
            {"zerotier": _svc_entry(exports_out=["networking", "peer"])},
        )
        new = _write_json(
            tmp_path / "new.json",
            {"zerotier": _svc_entry(exports_out=["networking"])},
        )
        result = diff_layers(
            LayerPaths(label="a", services_json=old),
            LayerPaths(label="b", services_json=new),
        )
        assert result.exports is not None
        assert len(result.exports.changes) == 1
        assert result.exports.changes[0].service == "zerotier"
        assert result.exports.changes[0].removed == ("peer",)

    def test_exports_none_without_services(self, tmp_path: Path) -> None:
        old_clan = _write_json(tmp_path / "old.json", {"a": OPTION_A})
        new_clan = _write_json(tmp_path / "new.json", {"a": OPTION_A})
        result = diff_layers(
            LayerPaths(label="a", clan_options=old_clan),
            LayerPaths(label="b", clan_options=new_clan),
        )
        assert result.exports is None

    def test_exports_section_rendered(self) -> None:
        ex = ExportDiff(
            old_label="25.11",
            new_label="main",
            changes=(ExportChange(service="zerotier", added=(), removed=("peer",)),),
        )
        text = format_multi_layer_diff(MultiLayerDiff(exports=ex))
        assert "## Service exports" in text
        assert "zerotier: -peer" in text

    def test_exports_section_after_services(self) -> None:
        svc = ServiceDiff(old_label="a", new_label="b", added=("pki",))
        ex = ExportDiff(
            old_label="a",
            new_label="b",
            changes=(ExportChange(service="zerotier", added=("x",), removed=()),),
        )
        text = format_multi_layer_diff(MultiLayerDiff(services=svc, exports=ex))
        assert text.index("## Services") < text.index("## Service exports")


def _write_templates(
    base: Path,
    manifest: dict[str, dict[str, dict[str, Any]]],
) -> Path:
    """Materialize template dirs + a manifest JSON pointing at them.

    ``manifest`` maps category -> name -> {"description": str, "files": {rel: content}}.
    Returns the path to a manifest JSON in the flake-output shape
    ``{category: {name: {description, path}}}``.
    """
    base.mkdir(parents=True, exist_ok=True)
    out: dict[str, Any] = {}
    for category, names in manifest.items():
        out[category] = {}
        for name, spec in names.items():
            tdir = base / "templates" / category / name
            tdir.mkdir(parents=True, exist_ok=True)
            files: dict[str, str] = spec.get("files", {})
            for rel, content in files.items():
                fpath = tdir / rel
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content)
            out[category][name] = {
                "description": spec.get("description", ""),
                "path": str(tdir),
            }
    return _write_json(base / "templates.json", out)


class TestLoadTemplates:
    def test_flattens_to_category_name(self, tmp_path: Path) -> None:
        manifest = _write_templates(
            tmp_path / "v",
            {
                "clan": {"default": {"description": "d", "files": {"flake.nix": "x"}}},
                "disko": {"ext4": {"description": "e", "files": {}}},
            },
        )
        result = load_templates(manifest)
        assert set(result) == {"clan/default", "disko/ext4"}
        assert result["clan/default"].description == "d"
        assert isinstance(result["clan/default"], TemplateInfo)
        assert result["clan/default"].path.is_dir()

    def test_skips_entry_without_path(self, tmp_path: Path) -> None:
        p = _write_json(
            tmp_path / "m.json",
            {"clan": {"broken": {"description": "no path"}}},
        )
        assert load_templates(p) == {}

    def test_skips_non_dict_category(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "m.json", {"clan": "not-a-dict"})
        assert load_templates(p) == {}

    def test_rejects_non_object(self, tmp_path: Path) -> None:
        p = _write_json(tmp_path / "bad.json", [1, 2])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="Expected top-level JSON object"):
            load_templates(p)


class TestDiffTemplates:
    def test_identical(self, tmp_path: Path) -> None:
        t = load_templates(
            _write_templates(
                tmp_path / "v",
                {"clan": {"default": {"description": "d", "files": {"a.nix": "1"}}}},
            )
        )
        result = diff_templates(t, t)
        assert not result.has_changes

    def test_added(self, tmp_path: Path) -> None:
        old = load_templates(_write_templates(tmp_path / "old", {}))
        new = load_templates(
            _write_templates(
                tmp_path / "new",
                {"clan": {"default": {"description": "d", "files": {"a": "1"}}}},
            )
        )
        result = diff_templates(old, new, old_label="25.11", new_label="main")
        assert result.added == ("clan/default",)
        assert result.removed == ()
        assert result.old_label == "25.11"
        assert result.new_label == "main"

    def test_removed(self, tmp_path: Path) -> None:
        old = load_templates(
            _write_templates(
                tmp_path / "old",
                {"machine": {"new-machine": {"description": "m", "files": {"a": "1"}}}},
            )
        )
        new = load_templates(_write_templates(tmp_path / "new", {}))
        result = diff_templates(old, new)
        assert result.removed == ("machine/new-machine",)
        assert result.added == ()

    def test_description_change(self, tmp_path: Path) -> None:
        old = load_templates(
            _write_templates(
                tmp_path / "old",
                {"clan": {"default": {"description": "old desc", "files": {"a": "1"}}}},
            )
        )
        new = load_templates(
            _write_templates(
                tmp_path / "new",
                {"clan": {"default": {"description": "new desc", "files": {"a": "1"}}}},
            )
        )
        result = diff_templates(old, new)
        assert len(result.description_changed) == 1
        dc = result.description_changed[0]
        assert dc.template == "clan/default"
        assert dc.old == "old desc"
        assert dc.new == "new desc"
        assert result.content_changed == ()

    def test_content_change_added_removed_modified(self, tmp_path: Path) -> None:
        old = load_templates(
            _write_templates(
                tmp_path / "old",
                {
                    "clan": {
                        "default": {
                            "description": "d",
                            "files": {
                                "keep.nix": "same",
                                "mod.nix": "before",
                                "gone.nix": "x",
                            },
                        }
                    }
                },
            )
        )
        new = load_templates(
            _write_templates(
                tmp_path / "new",
                {
                    "clan": {
                        "default": {
                            "description": "d",
                            "files": {
                                "keep.nix": "same",
                                "mod.nix": "after",
                                "fresh.nix": "y",
                            },
                        }
                    }
                },
            )
        )
        result = diff_templates(old, new)
        assert result.description_changed == ()
        assert len(result.content_changed) == 1
        cc = result.content_changed[0]
        assert cc.template == "clan/default"
        assert cc.added_files == ("fresh.nix",)
        assert cc.removed_files == ("gone.nix",)
        assert cc.modified_files == ("mod.nix",)

    def test_nested_files_relative_keys(self, tmp_path: Path) -> None:
        """Content compared by path relative to template root, not absolute."""
        old = load_templates(
            _write_templates(
                tmp_path / "old",
                {"clan": {"d": {"description": "x", "files": {"sub/a.nix": "1"}}}},
            )
        )
        new = load_templates(
            _write_templates(
                tmp_path / "new",
                {"clan": {"d": {"description": "x", "files": {"sub/a.nix": "2"}}}},
            )
        )
        result = diff_templates(old, new)
        assert result.content_changed[0].modified_files == ("sub/a.nix",)

    def test_unchanged_template_no_content_change(self, tmp_path: Path) -> None:
        old = load_templates(
            _write_templates(
                tmp_path / "old",
                {"clan": {"d": {"description": "x", "files": {"a": "1", "b": "2"}}}},
            )
        )
        new = load_templates(
            _write_templates(
                tmp_path / "new",
                {"clan": {"d": {"description": "x", "files": {"b": "2", "a": "1"}}}},
            )
        )
        result = diff_templates(old, new)
        assert not result.has_changes

    def test_results_sorted(self, tmp_path: Path) -> None:
        old = load_templates(
            _write_templates(
                tmp_path / "old",
                {"clan": {"z": {"files": {"a": "1"}}, "a": {"files": {"a": "1"}}}},
            )
        )
        new = load_templates(
            _write_templates(
                tmp_path / "new",
                {"clan": {"m": {"files": {"a": "1"}}, "a": {"files": {"a": "1"}}}},
            )
        )
        result = diff_templates(old, new)
        assert result.added == ("clan/m",)
        assert result.removed == ("clan/z",)


class TestFormatTemplateDiff:
    def test_no_changes(self) -> None:
        text = format_template_diff(TemplateDiff(old_label="25.11", new_label="main"))
        assert "No template changes" in text
        assert "25.11" in text
        assert "main" in text

    def test_with_changes(self) -> None:
        result = TemplateDiff(
            old_label="25.11",
            new_label="main",
            added=("clan/new",),
            removed=("disko/old",),
            description_changed=(
                DescriptionChange(template="clan/default", old="a", new="b"),
            ),
            content_changed=(
                TemplateContentChange(
                    template="machine/new-machine",
                    added_files=("added.nix",),
                    removed_files=("removed.nix",),
                    modified_files=("flake.nix",),
                ),
            ),
        )
        text = format_template_diff(result)
        assert "Templates diff: 25.11 -> main" in text
        assert "Summary: +1 -1 desc~1 content~1" in text
        assert _section_items(text, "Added") == ["clan/new"]
        assert _section_items(text, "Removed") == ["disko/old"]
        assert _section_items(text, "Description changed") == ["clan/default: a -> b"]
        assert "machine/new-machine:" in text
        assert "+added.nix" in text
        assert "~flake.nix" in text
        assert "-removed.nix" in text

    def test_summary_before_sections(self) -> None:
        result = TemplateDiff(old_label="a", new_label="b", added=("clan/x",))
        text = format_template_diff(result)
        assert text.index("Summary:") < text.index("Added")


class TestDiffLayersTemplates:
    def test_templates_via_layers(self, tmp_path: Path) -> None:
        old = _write_templates(
            tmp_path / "old",
            {"clan": {"default": {"description": "d", "files": {"a": "1"}}}},
        )
        new = _write_templates(
            tmp_path / "new",
            {"clan": {"default": {"description": "d", "files": {"a": "2"}}}},
        )
        result = diff_layers(
            LayerPaths(label="a", templates_json=old),
            LayerPaths(label="b", templates_json=new),
        )
        assert result.templates is not None
        assert result.templates.content_changed[0].template == "clan/default"
        assert result.clan is None

    def test_templates_none_without_manifest(self, tmp_path: Path) -> None:
        old_clan = _write_json(tmp_path / "old.json", {"a": OPTION_A})
        new_clan = _write_json(tmp_path / "new.json", {"a": OPTION_A})
        result = diff_layers(
            LayerPaths(label="a", clan_options=old_clan),
            LayerPaths(label="b", clan_options=new_clan),
        )
        assert result.templates is None

    def test_rejects_asymmetric_templates(self, tmp_path: Path) -> None:
        old = _write_templates(tmp_path / "old", {})
        with pytest.raises(ValueError, match=r"templates.*old.*provided.*new.*missing"):
            diff_layers(
                LayerPaths(label="old", templates_json=old),
                LayerPaths(label="new"),
            )

    def test_templates_section_rendered(self) -> None:
        diff = MultiLayerDiff(
            templates=TemplateDiff(
                old_label="25.11",
                new_label="main",
                added=("clan/new",),
            )
        )
        text = format_multi_layer_diff(diff)
        assert "## Templates" in text
        assert "clan/new" in text

    def test_templates_section_after_options(self) -> None:
        clan_result = DiffResult(
            old_label="a",
            new_label="b",
            added=(OptionDiff(name="clan.x", kind=ChangeKind.ADDED),),
        )
        templates = TemplateDiff(old_label="a", new_label="b", added=("clan/new",))
        text = format_multi_layer_diff(
            MultiLayerDiff(clan=clan_result, templates=templates)
        )
        assert text.index("## Clan") < text.index("## Templates")
