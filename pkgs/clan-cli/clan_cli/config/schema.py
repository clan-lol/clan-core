import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from fastapi import HTTPException

from clan_cli.dirs import (
    nixpkgs_source,
    specific_flake_dir,
)
from clan_cli.errors import ClanError
from clan_cli.nix import nix_eval

from ..types import FlakeName


def machine_schema(
    flake_name: FlakeName,
    config: dict,
    clan_imports: Optional[list[str]] = None,
) -> dict:
    flake = specific_flake_dir(flake_name)
    # use nix eval to lib.evalModules .#nixosConfigurations.<machine_name>.options.clan
    with NamedTemporaryFile(mode="w", dir=flake) as clan_machine_settings_file:
        env = os.environ.copy()
        if clan_imports is not None:
            config["clanImports"] = clan_imports
        # dump config to file
        json.dump(config, clan_machine_settings_file, indent=2)
        clan_machine_settings_file.seek(0)
        env["CLAN_MACHINE_SETTINGS_FILE"] = clan_machine_settings_file.name
        # ensure that the requested clanImports exist
        proc = subprocess.run(
            nix_eval(
                flags=[
                    "--impure",
                    "--show-trace",
                    "--expr",
                    f"""
                    let
                        b = builtins;
                        # hardcoding system for now, not sure where to get it from
                        system = "x86_64-linux";
                        flake = b.getFlake (toString {flake});
                        clan-core = flake.inputs.clan-core;
                        config = b.fromJSON (b.readFile (b.getEnv "CLAN_MACHINE_SETTINGS_FILE"));
                        modules_not_found =
                            b.filter
                            (modName: ! clan-core.clanModules ? ${{modName}})
                            config.clanImports or [];
                    in
                        modules_not_found
                    """,
                ]
            ),
            capture_output=True,
            text=True,
            cwd=flake,
            env=env,
        )
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            raise ClanError(
                f"Failed to check clanImports for existence:\n{proc.stderr}"
            )
        modules_not_found = json.loads(proc.stdout)
        if len(modules_not_found) > 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": "Some requested clan modules could not be found",
                    "modules_not_found": modules_not_found,
                },
            )

        # get the schema
        proc = subprocess.run(
            nix_eval(
                flags=[
                    "--impure",
                    "--show-trace",
                    "--expr",
                    f"""
                    let
                        # hardcoding system for now, not sure where to get it from
                        system = "x86_64-linux";
                        flake = builtins.getFlake (toString {flake});
                        clan-core = flake.inputs.clan-core;
                        nixpkgsSrc = flake.inputs.nixpkgs or {nixpkgs_source()};
                        lib = import (nixpkgsSrc + /lib);
                        pkgs = import nixpkgsSrc {{ inherit system; }};
                        config = lib.importJSON (builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE");
                        fakeMachine = pkgs.nixos {{
                            imports =
                                [
                                    clan-core.nixosModules.clanCore
                                    # potentially the config might affect submodule options,
                                    #   therefore we need to import it
                                    config
                                ]
                                # add all clan modules specified via clanImports
                                ++ (map (name: clan-core.clanModules.${{name}}) config.clanImports or []);
                        }};
                        clanOptions = fakeMachine.options.clan;
                        jsonschemaLib = import {Path(__file__).parent / "jsonschema"} {{ inherit lib; }};
                        jsonschema = jsonschemaLib.parseOptions clanOptions;
                    in
                        jsonschema
                    """,
                ],
            ),
            capture_output=True,
            text=True,
            cwd=flake,
            env=env,
        )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise ClanError(f"Failed to read schema:\n{proc.stderr}")
    return json.loads(proc.stdout)
