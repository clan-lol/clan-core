import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

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
        inject_config_flags = []
        if clan_imports is not None:
            config["clanImports"] = clan_imports
        json.dump(config, clan_machine_settings_file, indent=2)
        clan_machine_settings_file.seek(0)
        env["CLAN_MACHINE_SETTINGS_FILE"] = clan_machine_settings_file.name
        inject_config_flags = [
            "--impure",  # needed to access CLAN_MACHINE_SETTINGS_FILE
        ]
        proc = subprocess.run(
            nix_eval(
                flags=inject_config_flags
                + [
                    "--impure",
                    "--show-trace",
                    "--expr",
                    f"""
                    let
                        system = builtins.currentSystem;
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
