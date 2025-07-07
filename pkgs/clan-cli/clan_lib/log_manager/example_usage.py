#!/usr/bin/env python3
"""
Simple LogManager example with filter function.

This demonstrates:
- Dynamic group names with URL encoding
- Hierarchical structure navigation using the filter function
- Pattern: clans -> <dynamic_name> -> machines -> <dynamic_name>
"""

from pathlib import Path

from clan_lib.log_manager import LogGroupConfig, LogManager


def example_function() -> None:
    """Example function for creating logs."""


def run_machine_deploy() -> None:
    """Function for deploying machines."""


def main() -> None:
    """Simple LogManager demonstration with filter function."""
    # Setup
    log_manager = LogManager(base_dir=Path("/tmp/clan_logs"))

    # Configure structure: clans -> <dynamic> -> machines -> <dynamic>
    clans_config = LogGroupConfig("clans", "Clans")
    machines_config = LogGroupConfig("machines", "Machines")
    clans_config = clans_config.add_child(machines_config)
    log_manager = log_manager.add_root_group_config(clans_config)

    print("=== LogManager Filter Function Example ===\n")

    # Create some example logs
    repos = ["/home/user/Projects/qubasas_clan", "https://github.com/qubasa/myclan"]
    machines = ["wintux", "demo", "gchq-local"]

    for repo in repos:
        for machine in machines:
            log_manager.create_log_file(
                run_machine_deploy,
                f"deploy_{machine}",
                ["clans", repo, "machines", machine],
            )

    print("Created log files for multiple repos and machines\n")

    # Demonstrate filter function
    print("=== Using the filter() function ===")

    # 1. List top-level groups
    top_level = log_manager.filter([])
    print(f"1. Top-level groups: {top_level}")

    # 2. List all repositories under 'clans'
    clans_repos = log_manager.filter(["clans"])
    print(f"2. Repositories under clans: {clans_repos}")

    # 3. List machines under first repository
    if clans_repos:
        first_repo = clans_repos[0]
        repo_machines = log_manager.filter(["clans", first_repo, "machines"])
        print(f"3. Machines under '{first_repo}': {repo_machines}")

    # 4. List machines under second repository
    if len(clans_repos) > 1:
        second_repo = clans_repos[1]
        repo_machines = log_manager.filter(["clans", second_repo, "machines"])
        print(f"4. Machines under '{second_repo}': {repo_machines}")

    print("\n=== Using get_log_file with arrays ===")
    # Demonstrate the new array-based get_log_file functionality
    if clans_repos and len(clans_repos) > 0:
        specific_log = log_manager.get_log_file(
            "deploy_wintux",
            selector=["clans", clans_repos[0], "machines", "wintux"],
        )
        if specific_log:
            print(
                f"5. Found specific log: {specific_log.op_key} in {specific_log.func_name}"
            )
        else:
            print("5. Specific log not found")

    print("\n=== Key Features ===")
    print("✓ Dynamic names with special chars (/, spaces, etc.) work")
    print("✓ Names are URL encoded in filesystem but returned decoded")
    print("✓ Filter function navigates hierarchy with simple arrays")
    print("✓ get_log_file now accepts specific_group as array")
    print("✓ Empty array [] lists top-level groups")
    print("✓ Odd indices are dynamic, even indices are structure")


if __name__ == "__main__":
    main()
