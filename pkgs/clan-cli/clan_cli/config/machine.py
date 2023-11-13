import json
import os
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from fastapi import HTTPException

from clan_cli.dirs import (
    machine_settings_file,
    specific_flake_dir,
    specific_machine_dir,
)
from clan_cli.errors import ClanError
from clan_cli.git import commit_file
from clan_cli.nix import nix_eval

from ..types import FlakeName


def verify_machine_config(
    flake_name: FlakeName,
    machine_name: str,
    config: Optional[dict] = None,
    flake: Optional[Path] = None,
) -> Optional[str]:
    """
    Verify that the machine evaluates successfully
    Returns a tuple of (success, error_message)
    """
    if config is None:
        config = config_for_machine(flake_name, machine_name)
    flake = specific_flake_dir(flake_name)
    with NamedTemporaryFile(mode="w", dir=flake) as clan_machine_settings_file:
        json.dump(config, clan_machine_settings_file, indent=2)
        clan_machine_settings_file.seek(0)
        env = os.environ.copy()
        env["CLAN_MACHINE_SETTINGS_FILE"] = clan_machine_settings_file.name
        cmd = nix_eval(
            flags=[
                "--impure",
                "--show-trace",
                "--show-trace",
                "--impure",  # needed to access CLAN_MACHINE_SETTINGS_FILE
                f".#nixosConfigurations.{machine_name}.config.system.build.vm.outPath",
            ],
        )
        # repro_env_break(work_dir=flake, env=env, cmd=cmd)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=flake,
            env=env,
        )
    if proc.returncode != 0:
        return proc.stderr
    return None


def config_for_machine(flake_name: FlakeName, machine_name: str) -> dict:
    # read the config from a json file located at {flake}/machines/{machine_name}/settings.json
    if not specific_machine_dir(flake_name, machine_name).exists():
        raise HTTPException(
            status_code=404,
            detail=f"Machine {machine_name} not found. Create the machine first`",
        )
    settings_path = machine_settings_file(flake_name, machine_name)
    if not settings_path.exists():
        return {}
    with open(settings_path) as f:
        return json.load(f)


def set_config_for_machine(
    flake_name: FlakeName, machine_name: str, config: dict
) -> None:
    hostname_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
    if not re.match(hostname_regex, machine_name):
        raise ClanError("Machine name must be a valid hostname")
    if "networking" in config and "hostName" in config["networking"]:
        if machine_name != config["networking"]["hostName"]:
            raise HTTPException(
                status_code=400,
                detail="Machine name does not match the 'networking.hostName' setting in the config",
            )
        config["networking"]["hostName"] = machine_name
    # create machine folder if it doesn't exist
    # write the config to a json file located at {flake}/machines/{machine_name}/settings.json
    settings_path = machine_settings_file(flake_name, machine_name)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(config, f, indent=2)
    repo_dir = specific_flake_dir(flake_name)

    if repo_dir is not None:
        commit_file(settings_path, repo_dir)
