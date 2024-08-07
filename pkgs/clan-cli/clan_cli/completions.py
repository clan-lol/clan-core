import argparse
import json
import subprocess
import threading
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any

from .cmd import run
from .nix import nix_eval

"""
This module provides dynamic completions.
The completions should feel fast.
We target a maximum of 1second on our average machine.
"""


argcomplete: ModuleType | None = None
try:
    import argcomplete  # type: ignore[no-redef]
except ImportError:
    pass


# The default completion timeout for commands
COMPLETION_TIMEOUT: int = 3


def clan_dir(flake: str | None) -> str | None:
    from .dirs import get_clan_flake_toplevel_or_env

    path_result = get_clan_flake_toplevel_or_env()
    return str(path_result) if path_result is not None else None


def complete_machines(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for machine names configured in the clan.
    """
    machines: list[str] = []

    def run_cmd() -> None:
        try:
            if (clan_dir_result := clan_dir(None)) is not None:
                flake = clan_dir_result
            else:
                flake = "."
            services_result = json.loads(
                run(
                    nix_eval(
                        flags=[
                            f"{flake}#nixosConfigurations",
                            "--apply",
                            "builtins.attrNames",
                        ],
                    ),
                ).stdout.strip()
            )

            machines.extend(services_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    machines_dict = {name: "machine" for name in machines}
    return machines_dict


def complete_services_for_machine(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for machine facts generation services.
    """
    services: list[str] = []
    # TODO: consolidate, if multiple machines are used
    machines: list[str] = parsed_args.machines

    def run_cmd() -> None:
        try:
            if (clan_dir_result := clan_dir(None)) is not None:
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
                ).stdout.strip()
            )

            services.extend(services_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    services_dict = {name: "service" for name in services}
    return services_dict


def complete_backup_providers_for_machine(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for machine backup providers.
    """
    providers: list[str] = []
    machine: str = parsed_args.machine

    def run_cmd() -> None:
        try:
            if (clan_dir_result := clan_dir(None)) is not None:
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
                ).stdout.strip()
            )

            providers.extend(providers_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    providers_dict = {name: "provider" for name in providers}
    return providers_dict


def complete_state_services_for_machine(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for machine state providers.
    """
    providers: list[str] = []
    machine: str = parsed_args.machine

    def run_cmd() -> None:
        try:
            if (clan_dir_result := clan_dir(None)) is not None:
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
                ).stdout.strip()
            )

            providers.extend(providers_result)
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=COMPLETION_TIMEOUT)

    if thread.is_alive():
        return iter([])

    providers_dict = {name: "service" for name in providers}
    return providers_dict


def complete_secrets(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for clan secrets
    """
    from .clan_uri import FlakeId
    from .secrets.secrets import ListSecretsOptions, list_secrets

    if (clan_dir_result := clan_dir(None)) is not None:
        flake = clan_dir_result
    else:
        flake = "."

    options = ListSecretsOptions(
        flake=FlakeId(flake),
        pattern=None,
    )

    secrets = list_secrets(options.flake.path, options.pattern)

    secrets_dict = {name: "secret" for name in secrets}
    return secrets_dict


def complete_users(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for clan users
    """
    from pathlib import Path

    from .secrets.users import list_users

    if (clan_dir_result := clan_dir(None)) is not None:
        flake = clan_dir_result
    else:
        flake = "."

    users = list_users(Path(flake))

    users_dict = {name: "user" for name in users}
    return users_dict


def complete_groups(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> Iterable[str]:
    """
    Provides completion functionality for clan groups
    """
    from pathlib import Path

    from .secrets.groups import list_groups

    if (clan_dir_result := clan_dir(None)) is not None:
        flake = clan_dir_result
    else:
        flake = "."

    groups_list = list_groups(Path(flake))
    groups = [group.name for group in groups_list]

    groups_dict = {name: "group" for name in groups}
    return groups_dict


def add_dynamic_completer(
    action: argparse.Action,
    completer: Callable[..., Iterable[str]],
) -> None:
    """
    Add a completion function to an argparse action, this will only be added,
    if the argcomplete module is loaded.
    """
    if argcomplete:
        # mypy doesn't check this correctly, so we ignore it
        action.completer = completer  # type: ignore[attr-defined]
