"""CLI entry point for clan-release-diff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clan_release_diff.options_diff import (
    diff_options,
    format_diff,
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

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "diff":
            _run_single(args)
    except (OSError, ValueError, TypeError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(_EXIT_ERROR)


def _run_single(args: argparse.Namespace) -> None:
    old = load_options(args.old)
    new = load_options(args.new)
    result = diff_options(old, new, old_label=args.old_label, new_label=args.new_label)
    sys.stdout.write(format_diff(result))
    sys.exit(_EXIT_NO_CHANGES if not result.has_changes else _EXIT_CHANGES)
