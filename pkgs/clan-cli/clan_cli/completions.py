import argparse
import contextlib
import json
import subprocess
import threading
from collections.abc import Callable, Iterable
from pathlib import Path
from types import ModuleType
from typing import Any

from clan_lib.cmd import run
from clan_lib.dirs import get_clan_flake_toplevel_or_env
from clan_lib.flake.flake import Flake
from clan_lib.nix import nix_eval
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.templates import list_templates

from .secrets.groups import list_groups
from .secrets.secrets import list_secrets
from .secrets.users import list_users

"""
This module provides dynamic completions.
The completions should feel fast.
We target a maximum of 1second on our average machine.
"""


argcomplete: ModuleType | None = None
with contextlib.suppress(ImportError):
    import argcomplete  # type: ignore[no-redef]


# The default completion timeout for commands
COMPLETION_TIMEOUT: int = 3


def clan_dir(flake: str | None) -> str | None:
    if flake is not None:
        return flake

    path_result = get_clan_flake_toplevel_or_env()
    return str(path_result) if path_result is not None else None


def complete_machines(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for machine names configured in the clan."""
    machines: list[str] = []

    def run_cmd() -> None:
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."

            inventory = InventoryStore(Flake(str(flake))).read()
            machines.extend(inventory.get("machines", {}).keys())

        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    return dict.fromkeys(machines, "machine")


def complete_services_for_machine(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for machine facts generation services."""
    services: list[str] = []
    # TODO: consolidate, if multiple machines are used
    machines: list[str] = parsed_args.machines

    def run_cmd() -> None:
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."
            services_result = json.loads(
                run(
                    nix_eval(
                        flags=[
                            f"{flake}#nixosConfigurations.{machines[0]}.config.clan.core.facts.services",
                            "--apply",
                            "builtins.attrNames",
                        ],
                    ),
                ).stdout.strip(),
            )

            services.extend(services_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    return dict.fromkeys(services, "service")


def complete_backup_providers_for_machine(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for machine backup providers."""
    providers: list[str] = []
    machine: str = parsed_args.machine

    def run_cmd() -> None:
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."
            providers_result = json.loads(
                run(
                    nix_eval(
                        flags=[
                            f"{flake}#nixosConfigurations.{machine}.config.clan.core.backups.providers",
                            "--apply",
                            "builtins.attrNames",
                        ],
                    ),
                ).stdout.strip(),
            )

            providers.extend(providers_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    return dict.fromkeys(providers, "provider")


def complete_state_services_for_machine(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for machine state providers."""
    providers: list[str] = []
    machine: str = parsed_args.machine

    def run_cmd() -> None:
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."
            providers_result = json.loads(
                run(
                    nix_eval(
                        flags=[
                            f"{flake}#nixosConfigurations.{machine}.config.clan.core.state",
                            "--apply",
                            "builtins.attrNames",
                        ],
                    ),
                ).stdout.strip(),
            )

            providers.extend(providers_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    return dict.fromkeys(providers, "service")


def complete_secrets(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for clan secrets"""
    flake = (
        clan_dir_result
        if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None)))
        is not None
        else "."
    )

    secrets = list_secrets(Flake(flake).path)

    return dict.fromkeys(secrets, "secret")


def complete_users(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for clan users"""
    flake = (
        clan_dir_result
        if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None)))
        is not None
        else "."
    )

    users = list_users(Path(flake))

    return dict.fromkeys(users, "user")


def complete_groups(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for clan groups"""
    flake = (
        clan_dir_result
        if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None)))
        is not None
        else "."
    )

    groups_list = list_groups(Path(flake))
    groups = [group.name for group in groups_list]

    return dict.fromkeys(groups, "group")


def complete_templates_disko(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for disko templates"""
    flake = (
        clan_dir_result
        if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None)))
        is not None
        else "."
    )

    list_all_templates = list_templates(Flake(flake))
    disko_template_list = list_all_templates.builtins.get("disko")
    if disko_template_list:
        disko_templates = list(disko_template_list)
        return dict.fromkeys(disko_templates, "disko")
    return []


def complete_templates_clan(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for clan templates"""
    flake = (
        clan_dir_result
        if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None)))
        is not None
        else "."
    )

    list_all_templates = list_templates(Flake(flake))
    clan_template_list = list_all_templates.builtins.get("clan")
    if clan_template_list:
        clan_templates = list(clan_template_list)
        return dict.fromkeys(clan_templates, "clan")
    return []


def complete_templates_machine(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for machine templates"""
    flake = (
        clan_dir_result
        if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None)))
        is not None
        else "."
    )

    list_all_templates = list_templates(Flake(flake))
    machine_template_list = list_all_templates.builtins.get("machine")
    if machine_template_list:
        machine_templates = list(machine_template_list)
        return dict.fromkeys(machine_templates, "machine")
    return []


def complete_vars_for_machine(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for variable names for a specific machine.
    Only completes vars that already exist in the vars directory on disk.
    This is fast as it only scans the filesystem without any evaluation.
    """
    machine_name = getattr(parsed_args, "machine", None)
    if not machine_name:
        return []

    if (clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))) is not None:
        flake_path = Path(clan_dir_result)
    else:
        flake_path = Path()

    vars_dir = flake_path / "vars" / "per-machine" / machine_name
    vars_list: list[str] = []

    if vars_dir.exists() and vars_dir.is_dir():
        try:
            for generator_dir in vars_dir.iterdir():
                if not generator_dir.is_dir():
                    continue

                generator_name = generator_dir.name

                for var_dir in generator_dir.iterdir():
                    if var_dir.is_dir():
                        var_name = var_dir.name
                        var_id = f"{generator_name}/{var_name}"
                        vars_list.append(var_id)

        except (OSError, PermissionError):
            pass

    return dict.fromkeys(vars_list, "var")


def complete_target_host(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for target_host for a specific machine"""
    target_hosts: list[str] = []
    machine: str = parsed_args.machine

    def run_cmd() -> None:
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."
            target_host_result = json.loads(
                run(
                    nix_eval(
                        flags=[
                            f"{flake}#nixosConfigurations.{machine}.config.clan.core.networking.targetHost",
                        ],
                    ),
                ).stdout.strip(),
            )

            target_hosts.append(target_host_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    return dict.fromkeys(target_hosts, "target_host")


def complete_tags(
    _prefix: str,
    parsed_args: argparse.Namespace,
    **_kwargs: Any,
) -> Iterable[str]:
    """Provides completion functionality for tags inside the inventory"""
    tags: list[str] = []
    threads = []

    def run_computed_tags_cmd() -> None:
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."

            inventory_store = InventoryStore(Flake(str(flake)))
            inventory = inventory_store.get_readonly_raw()
            if "tags" in inventory:
                tags.extend(inventory["tags"].keys())

        except subprocess.CalledProcessError:
            pass

    def run_machines_tags_cmd() -> None:
        machine_tags: list[str] = []
        try:
            if (
                clan_dir_result := clan_dir(getattr(parsed_args, "flake", None))
            ) is not None:
                flake = clan_dir_result
            else:
                flake = "."
            inventory_store = InventoryStore(Flake(str(flake)))
            inventory = inventory_store.get_readonly_raw()
            machine_tags_result = inventory.get("machines")
            if machine_tags_result is None:
                return

            for machine in machine_tags_result.values():
                machine_tags.extend(machine.get("tags", []))

            tags.extend(machine_tags)
        except subprocess.CalledProcessError:
            pass

    def start_thread(target_function: Callable) -> threading.Thread:
        thread = threading.Thread(target=target_function)
        thread.start()
        return thread

    functions_to_run = [
        run_computed_tags_cmd,
        run_machines_tags_cmd,
    ]

    threads = [start_thread(func) for func in functions_to_run]

    for thread in threads:
        thread.join(timeout=COMPLETION_TIMEOUT)

    if any(thread.is_alive() for thread in threads):
        return iter([])

    return dict.fromkeys(tags, "tag")


def add_dynamic_completer(
    action: argparse.Action,
    completer: Callable[..., Iterable[str]],
) -> None:
    """Add a completion function to an argparse action, this will only be added,
    if the argcomplete module is loaded.
    """
    if argcomplete:
        # mypy doesn't check this correctly, so we ignore it
        action.completer = completer  # type: ignore[attr-defined]
