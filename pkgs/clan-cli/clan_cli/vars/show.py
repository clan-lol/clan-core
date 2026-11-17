import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

from clan_cli.display import (
    BLUE,
    GREEN,
    MAGENTA,
    RED,
    YELLOW,
    build_filter_desc,
    colored,
    dim,
    print_tree_header,
    tree_branch,
)
from clan_lib.errors import ClanError
from clan_lib.flake import require_flake


def get_vars_data(flake_path: Path, capture_access: bool = False) -> dict[str, Any]:
    """Get vars from the vars directory.

    If capture_access is True, also captures which users/machines have access to each var.
    """
    vars_dir = flake_path / "vars"
    vars_data: dict[str, Any] = {
        "shared": {},
        "per-machine": defaultdict(dict),
        "per-export": defaultdict(dict),
    }

    if not vars_dir.exists():
        return vars_data

    shared_dir = vars_dir / "shared"
    if shared_dir.exists():
        vars_data["shared"] = scan_vars_dir(shared_dir, capture_access)

    per_machine_dir = vars_dir / "per-machine"
    if per_machine_dir.exists():
        for machine_dir in per_machine_dir.iterdir():
            if machine_dir.is_dir():
                vars_data["per-machine"][machine_dir.name] = scan_vars_dir(
                    machine_dir, capture_access
                )

    per_export_dir = vars_dir / "per-export"
    if per_export_dir.exists():
        for export_dir in per_export_dir.iterdir():
            if export_dir.is_dir():
                vars_data["per-export"][export_dir.name] = scan_vars_dir(
                    export_dir, capture_access
                )

    return vars_data


def scan_vars_dir(directory: Path, capture_access: bool = False) -> dict[str, Any]:
    """Scan a directory for service-scoped vars.

    Format: <service>/<var_name>/value or <service>/<var_name>/secret

    If capture_access is True, also captures which users/machines have access to each var.
    """
    vars_dict = {}

    # Process service directories
    for service_dir in directory.iterdir():
        # Skip hidden directories and non-directories
        if not service_dir.is_dir() or service_dir.name.startswith("."):
            continue

        # Process var directories within each service
        for var_dir in service_dir.iterdir():
            if not var_dir.is_dir():
                continue

            var_name = f"{service_dir.name}/{var_dir.name}"

            # Check for value file or secret file
            value_file = var_dir / "value"
            secret_file = var_dir / "secret"

            var_info: dict[str, Any] = {}

            if secret_file.exists():
                var_info = {
                    "type": "secret",
                    "value": "<encrypted>",
                }
            elif value_file.exists():
                try:
                    value = value_file.read_text().strip()
                    var_info = {
                        "type": "value",
                        "value": value,
                    }
                except OSError:
                    # Skip files we can't read but continue processing
                    pass

            if not var_info:
                continue

            if capture_access:
                # Check for user access (users are directories)
                users_dir = var_dir / "users"
                if users_dir.exists():
                    users_with_access = [
                        user_dir.name
                        for user_dir in users_dir.iterdir()
                        if user_dir.is_dir()
                    ]
                    if users_with_access:
                        var_info["users"] = users_with_access

                # Check for machine access (machines are directories)
                machines_dir = var_dir / "machines"
                if machines_dir.exists():
                    machines_with_access = [
                        machine_dir.name
                        for machine_dir in machines_dir.iterdir()
                        if machine_dir.is_dir()
                    ]
                    if machines_with_access:
                        var_info["machines"] = machines_with_access

            vars_dict[var_name] = var_info

    return vars_dict


def filter_by_access(vars_dict: dict, kind: str, name: str) -> dict:
    """Keep the vars that give `name` access. `kind` is "users" or "machines"."""
    return {
        var_name: var_info
        for var_name, var_info in vars_dict.items()
        if name in var_info.get(kind, [])
    }


def filter_scope_by_access(scope: dict, kind: str, name: str) -> dict:
    """Filter every entry of a scope by access and drop the entries left empty."""
    filtered = {}
    for entry, entry_vars in scope.items():
        accessible = filter_by_access(entry_vars, kind, name)
        if accessible:
            filtered[entry] = accessible
    return filtered


def apply_filters(vars_data: dict, args: argparse.Namespace) -> dict:
    """Apply filters to vars data."""
    filtered = {
        "shared": vars_data["shared"],
        "per-machine": vars_data["per-machine"],
        "per-export": vars_data["per-export"],
    }

    # Filter by --shared flag
    if getattr(args, "shared", False):
        filtered["per-machine"] = {}
        filtered["per-export"] = {}

    # Filter vars by specific user
    if hasattr(args, "user") and args.user:
        filtered["shared"] = filter_by_access(filtered["shared"], "users", args.user)
        filtered["per-machine"] = filter_scope_by_access(
            filtered["per-machine"], "users", args.user
        )
        filtered["per-export"] = filter_scope_by_access(
            filtered["per-export"], "users", args.user
        )

    # Filter by specific machine (shows vars the machine has access to)
    if hasattr(args, "machine") and args.machine:
        filtered["shared"] = filter_by_access(
            filtered["shared"], "machines", args.machine
        )

        # Show the machine's own vars in full, plus vars of other machines it can read
        filtered_machines = {}
        for machine_name, machine_vars in filtered["per-machine"].items():
            if machine_name == args.machine:
                filtered_machines[machine_name] = machine_vars
                continue
            accessible = filter_by_access(machine_vars, "machines", args.machine)
            if accessible:
                filtered_machines[machine_name] = accessible
        filtered["per-machine"] = filtered_machines

        filtered["per-export"] = filter_scope_by_access(
            filtered["per-export"], "machines", args.machine
        )

    return filtered


def print_tree(vars_data: dict, filters: str = "") -> None:
    """Display vars in tree format."""
    print_tree_header("Vars", filters)

    has_content = False

    # Shared vars
    if vars_data["shared"]:
        has_content = True
        print(f"\n{colored('Shared', YELLOW)}")
        print_vars_tree(vars_data["shared"], indent="  ")

    # Per-machine vars
    if vars_data["per-machine"]:
        has_content = True
        print(f"\n{colored('Per-Machine', YELLOW)}")
        print_scope_tree(vars_data["per-machine"], BLUE)

    # Per-export vars
    if vars_data["per-export"]:
        has_content = True
        print(f"\n{colored('Per-Export', YELLOW)}")
        print_scope_tree(vars_data["per-export"], GREEN)

    if not has_content:
        print(dim("  No vars found"))


def print_scope_tree(scope: dict, name_color: str) -> None:
    """Print one scope: every entry with its vars below it."""
    entries = sorted(scope.items())
    for i, (entry, entry_vars) in enumerate(entries):
        is_last = i == len(entries) - 1
        branch, prefix = tree_branch(is_last)
        print(f"  {branch}{colored(entry, name_color)}")
        if entry_vars:
            print_vars_tree(entry_vars, indent=prefix)
        else:
            child_branch, _ = tree_branch(True)
            print(f"{prefix}{child_branch}{dim('(no vars)')}")


def print_vars_tree(vars_dict: dict, indent: str = "") -> None:
    """Print vars as a tree."""
    vars_list = sorted(vars_dict.items())
    for i, (name, info) in enumerate(vars_list):
        is_last = i == len(vars_list) - 1
        branch, _ = tree_branch(is_last)

        # Color based on type
        var_type = info.get("type", "unknown")
        name_color = RED if var_type == "secret" else MAGENTA

        # Build display text based on type
        if var_type == "value" and info.get("value"):
            # For values, show the name normally and the value dimmed
            value_str = str(info["value"])
            var_text = f"{colored(name, name_color)} {dim(value_str)}"
        elif var_type == "secret":
            # For secrets, just show the name
            var_text = colored(name, name_color)
        else:
            # Default: just the name
            var_text = colored(name, name_color)

        print(f"{indent}{branch}{var_text}")


def show_command(args: argparse.Namespace) -> None:
    """Main command to show vars."""
    try:
        flake = require_flake(getattr(args, "flake", None))
    except Exception as e:
        msg = "Failed to access flake"
        raise ClanError(msg, description=str(e)) from e

    # Check if we need to capture user/machine access info
    capture_access = bool(
        (hasattr(args, "user") and args.user)
        or (hasattr(args, "machine") and args.machine)
    )

    # Get vars data
    try:
        vars_data = get_vars_data(flake.path, capture_access=capture_access)
    except Exception as e:
        msg = "Failed to retrieve vars information"
        raise ClanError(msg, description=f"Error reading vars directory: {e}") from e

    # Apply filters
    vars_data = apply_filters(vars_data, args)

    # Build filter description
    filter_attrs = []
    if getattr(args, "shared", False):
        filter_attrs.append("shared")
    filter_attrs.extend(["user", "machine"])
    filter_desc = build_filter_desc(args, filter_attrs)

    # Display in tree format
    print_tree(vars_data, filter_desc)


def register_show_parser(parser: argparse.ArgumentParser) -> None:
    """Register the show subcommand."""
    parser.add_argument(
        "--shared",
        action="store_true",
        help="Show only shared vars",
    )
    parser.add_argument("--user", help="Filter by specific user")
    parser.add_argument("--machine", help="Filter by specific machine")
    parser.set_defaults(func=show_command)
