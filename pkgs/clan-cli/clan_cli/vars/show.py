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
        "per-user": defaultdict(dict),
        "per-machine": defaultdict(dict),
    }

    if not vars_dir.exists():
        return vars_data

    shared_dir = vars_dir / "shared"
    if shared_dir.exists():
        vars_data["shared"] = scan_vars_dir(shared_dir, capture_access)

    per_user_dir = vars_dir / "per-user"
    if per_user_dir.exists():
        for user_dir in per_user_dir.iterdir():
            if user_dir.is_dir():
                vars_data["per-user"][user_dir.name] = scan_vars_dir(
                    user_dir, capture_access
                )

    per_machine_dir = vars_dir / "per-machine"
    if per_machine_dir.exists():
        for machine_dir in per_machine_dir.iterdir():
            if machine_dir.is_dir():
                vars_data["per-machine"][machine_dir.name] = scan_vars_dir(
                    machine_dir, capture_access
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


def apply_filters(vars_data: dict, args: argparse.Namespace) -> dict:
    """Apply filters to vars data."""
    filtered = {
        "shared": vars_data["shared"],
        "per-user": vars_data["per-user"],
        "per-machine": vars_data["per-machine"],
    }

    # Filter by --shared flag
    if getattr(args, "shared", False):
        filtered["per-user"] = {}
        filtered["per-machine"] = {}

    # Filter vars by specific user
    if hasattr(args, "user") and args.user:
        # Filter per-user vars to only show that user's directory
        filtered["per-user"] = {
            k: v for k, v in filtered["per-user"].items() if k == args.user
        }

        # Filter shared vars to only show those the user has access to
        if filtered["shared"]:
            filtered["shared"] = {
                var_name: var_info
                for var_name, var_info in filtered["shared"].items()
                if "users" in var_info and args.user in var_info["users"]
            }

        # Filter per-machine vars to only show those the user has access to
        filtered_machines = {}
        for machine_name, machine_vars in filtered["per-machine"].items():
            filtered_machine_vars = {
                var_name: var_info
                for var_name, var_info in machine_vars.items()
                if "users" in var_info and args.user in var_info["users"]
            }
            if filtered_machine_vars:
                filtered_machines[machine_name] = filtered_machine_vars
        filtered["per-machine"] = filtered_machines

    # Filter by specific machine (shows vars the machine has access to)
    if hasattr(args, "machine") and args.machine:
        # Filter shared vars to only show those the machine has access to
        if filtered["shared"]:
            filtered["shared"] = {
                var_name: var_info
                for var_name, var_info in filtered["shared"].items()
                if "machines" in var_info and args.machine in var_info["machines"]
            }

        # Filter per-machine vars to show the specific machine and vars it has access to in other machines
        filtered_machines = {}
        for machine_name, machine_vars in filtered["per-machine"].items():
            if machine_name == args.machine:
                # Include all vars for this specific machine
                filtered_machines[machine_name] = machine_vars
            else:
                # For other machines, only include vars this machine has access to
                filtered_machine_vars = {}
                for var_name, var_info in machine_vars.items():
                    if "machines" in var_info and args.machine in var_info["machines"]:
                        filtered_machine_vars[var_name] = var_info
                if filtered_machine_vars:
                    filtered_machines[machine_name] = filtered_machine_vars
        filtered["per-machine"] = filtered_machines

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

    # Per-user vars
    if vars_data["per-user"]:
        has_content = True
        print(f"\n{colored('Per-User', YELLOW)}")
        users_list = sorted(vars_data["per-user"].items())
        for i, (user, user_vars) in enumerate(users_list):
            is_last = i == len(users_list) - 1
            branch, prefix = tree_branch(is_last)
            print(f"  {branch}{colored(user, GREEN)}")
            if user_vars:
                print_vars_tree(user_vars, indent=prefix)
            else:
                child_branch, _ = tree_branch(True)
                print(f"{prefix}{child_branch}{dim('(no vars)')}")

    # Per-machine vars
    if vars_data["per-machine"]:
        has_content = True
        print(f"\n{colored('Per-Machine', YELLOW)}")
        machines_list = sorted(vars_data["per-machine"].items())
        for i, (machine, machine_vars) in enumerate(machines_list):
            is_last = i == len(machines_list) - 1
            branch, prefix = tree_branch(is_last)
            print(f"  {branch}{colored(machine, BLUE)}")
            if machine_vars:
                print_vars_tree(machine_vars, indent=prefix)
            else:
                child_branch, _ = tree_branch(True)
                print(f"{prefix}{child_branch}{dim('(no vars)')}")

    if not has_content:
        print(dim("  No vars found"))


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
