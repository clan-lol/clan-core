"""Tests for clan_release_diff.options_diff."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

import pytest
from clan_release_diff.options_diff import (
    ChangeKind,
    DiffResult,
    LayerPaths,
    MultiLayerDiff,
    OptionDiff,
    diff_layers,
    diff_options,
    format_diff,
    format_multi_layer_diff,
    load_options,
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
