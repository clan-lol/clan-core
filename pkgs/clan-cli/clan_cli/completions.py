import argparse
import json
import subprocess
import threading
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any

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
            # In my tests this was consistently faster than:
            # nix eval .#nixosConfigurations --apply builtins.attrNames
            cmd = ["nix", "flake", "show", "--system", "no-eval", "--json"]
            if (clan_dir_result := clan_dir(None)) is not None:
                cmd.append(clan_dir_result)
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )

            data = json.loads(result.stdout)
            try:
                machines.extend(data.get("nixosConfigurations").keys())
            except KeyError:
                pass
        except subprocess.CalledProcessError:
            pass

    thread = threading.Thread(target=run_cmd)
    thread.start()
    thread.join(timeout=3)

    if thread.is_alive():
        return iter([])

    machines_dict = {name: "machine" for name in machines}
    return machines_dict


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
