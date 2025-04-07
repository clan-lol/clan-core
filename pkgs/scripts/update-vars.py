#! /usr/bin/env python3

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from clan_cli.flake import Flake
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_build, nix_config, nix_eval
from clan_cli.vars.generate import generate_vars
from clan_cli.vars.keygen import keygen

if _project_root := os.environ.get("PRJ_ROOT"):
    clan_core_dir = Path(_project_root)
else:
    msg = "PRJ_ROOT not set. Enter the dev environment first"
    raise Exception(msg)  # noqa TRY002

test_name = "dummy-inventory-test"


def _test_dir(test_name: str) -> Path:
    return Path(clan_core_dir / "checks" / test_name)


def machine_names(test_name: str) -> list[str]:
    """
    Get the machine names from the test flake
    """
    cmd = nix_eval(
        [
            f"{clan_core_dir}#checks.{nix_config()['system']}.{test_name}.nodes",
            "--apply",
            "builtins.attrNames",
        ]
    )
    out = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(out.stdout.strip())


class TestMachine(Machine):
    """
    Machine class which is able to deal with not having an actual flake.
    All nix build and eval calls will be forwarded to:
      clan-core#checks.<system>.<test_name>.nodes.<machine_name>.<attr>
    """

    @property
    def deployment(self) -> dict:
        if getattr(self, "_deployment", None):
            return self._deployment
        cmd = nix_build(
            [
                f"{clan_core_dir}#checks.{nix_config()['system']}.{test_name}.nodes.{self.name}.system.clan.deployment.file"
            ]
        )
        out = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        self._deployment = json.loads(Path(out.stdout.strip()).read_text())
        return self._deployment

    def eval_nix(
        self,
        attr: str,
        refresh: bool = False,
        extra_config: None | dict = None,
        nix_options: list[str] | None = None,
    ) -> Any:
        """
        eval a nix attribute of the machine
        @attr: the attribute to get
        """

        if nix_options is None:
            nix_options = []

        # return self.nix("eval", attr, nix_options)
        cmd = nix_eval(
            [
                f"{clan_core_dir}#checks.{nix_config()['system']}.{test_name}.nodes.{self.name}.{attr}"
            ]
        )
        out = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        return json.loads(out.stdout.strip())

    def build_nix(
        self,
        attr: str,
        extra_config: None | dict = None,
        nix_options: list[str] | None = None,
    ) -> Path:
        """
        build a nix attribute of the machine
        @attr: the attribute to get
        """

        if nix_options is None:
            nix_options = []

        cmd = nix_build(
            [
                f"{clan_core_dir}#checks.{nix_config()['system']}.{test_name}.nodes.{self.name}.{attr}"
            ]
        )
        out = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        return Path(out.stdout.strip())

    def flush_caches(self) -> None:
        """
        Disable flush, because it calls prefetch() which resets the overridden Flake._path
        """
        return


if __name__ == "__main__":
    os.environ["CLAN_NO_COMMIT"] = "1"
    test_dir = _test_dir(test_name)
    subprocess.run(["rm", "-rf", f"{test_dir}/vars", f"{test_dir}/sops"])
    flake = Flake(str(test_dir))
    flake._path = test_dir  # noqa SLF001
    flake._is_local = True  # noqa SLF001
    machines = [TestMachine(name, flake) for name in machine_names(test_name)]
    user = "admin"
    if not Path(flake.path / "sops" / "users" / user / "key.json").exists():
        keygen(user, flake, False)
    generate_vars(list(machines))
