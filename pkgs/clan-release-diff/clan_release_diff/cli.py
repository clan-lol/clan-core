"""CLI entry point for clan-release-diff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clan_release_diff.options_diff import (
    LayerPaths,
    diff_layers,
    diff_options,
    format_diff,
    format_multi_layer_diff,
    load_options,
)

# Exit codes following diff(1) convention:
#   0 = no differences
#   1 = differences found
#   2 = error
_EXIT_NO_CHANGES = 0
_EXIT_CHANGES = 1
_EXIT_ERROR = 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clan-release-diff",
        description="Diff NixOS/clan options.json files between two versions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- single: diff two options.json files directly ---
    single = sub.add_parser(
        "diff",
        help="Diff two options.json files.",
    )
    single.add_argument("old", type=Path, help="Path to old options.json")
    single.add_argument("new", type=Path, help="Path to new options.json")
    single.add_argument(
        "--old-label", default="old", help="Label for old version (default: old)"
    )
    single.add_argument(
        "--new-label", default="new", help="Label for new version (default: new)"
    )

    # -- layers: diff both clan and nixos layers at once ---
    layers = sub.add_parser(
        "layers",
        help="Diff clan and NixOS option layers between two versions.",
    )
    layers.add_argument("--old-label", required=True, help="Label for old version")
    layers.add_argument("--new-label", required=True, help="Label for new version")
    layers.add_argument("--old-clan", type=Path, help="Path to old clan options.json")
    layers.add_argument("--new-clan", type=Path, help="Path to new clan options.json")
    layers.add_argument(
        "--old-nixos", type=Path, help="Path to old NixOS (clan.core) options.json"
    )
    layers.add_argument(
        "--new-nixos", type=Path, help="Path to new NixOS (clan.core) options.json"
    )
    layers.add_argument(
        "--old-services", type=Path, help="Path to old clanModulesViaService info.json"
    )
    layers.add_argument(
        "--new-services", type=Path, help="Path to new clanModulesViaService info.json"
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "diff":
            _run_single(args)
        elif args.command == "layers":
            _run_layers(args)
    except (OSError, ValueError, TypeError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(_EXIT_ERROR)


def _run_single(args: argparse.Namespace) -> None:
    old = load_options(args.old)
    new = load_options(args.new)
    result = diff_options(old, new, old_label=args.old_label, new_label=args.new_label)
    sys.stdout.write(format_diff(result))
    sys.exit(_EXIT_NO_CHANGES if not result.has_changes else _EXIT_CHANGES)


def _run_layers(args: argparse.Namespace) -> None:
    old = LayerPaths(
        label=args.old_label,
        clan_options=args.old_clan,
        nixos_options=args.old_nixos,
        services_json=args.old_services,
    )
    new = LayerPaths(
        label=args.new_label,
        clan_options=args.new_clan,
        nixos_options=args.new_nixos,
        services_json=args.new_services,
    )
    result = diff_layers(old, new)
    sys.stdout.write(format_multi_layer_diff(result))

    has_changes = (
        (result.clan is not None and result.clan.has_changes)
        or (result.nixos is not None and result.nixos.has_changes)
        or (result.services is not None and result.services.has_changes)
    )
    sys.exit(_EXIT_NO_CHANGES if not has_changes else _EXIT_CHANGES)
