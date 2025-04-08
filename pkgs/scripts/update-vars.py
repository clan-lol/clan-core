#! /usr/bin/env python3

import argparse
import json
import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from clan_cli.flake import Flake
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_build, nix_config, nix_eval
from clan_cli.vars.generate import generate_vars

if _project_root := os.environ.get("PRJ_ROOT"):
    clan_core_dir = Path(_project_root)
else:
    msg = "PRJ_ROOT not set. Enter the dev environment first"
    raise Exception(msg)  # noqa TRY002

sops_priv_key = (
    "AGE-SECRET-KEY-1PL0M9CWRCG3PZ9DXRTTLMCVD57U6JDFE8K7DNVQ35F4JENZ6G3MQ0RQLRV"
)
sops_pub_key = "age1qm0p4vf9jvcnn43s6l4prk8zn6cx0ep9gzvevxecv729xz540v8qa742eg"


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

    def __init__(self, name: str, flake: Flake, test_name: str) -> None:
        super().__init__(name, flake)
        self.test_name = test_name

    @property
    def deployment(self) -> dict:
        if getattr(self, "_deployment", None):
            return self._deployment
        cmd = nix_build(
            [
                f"{clan_core_dir}#checks.{nix_config()['system']}.{self.test_name}.nodes.{self.name}.system.clan.deployment.file"
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
                f"{clan_core_dir}#checks.{nix_config()['system']}.{self.test_name}.nodes.{self.name}.{attr}"
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
                f"{clan_core_dir}#checks.{nix_config()['system']}.{self.test_name}.nodes.{self.name}.{attr}"
            ]
        )
        out = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        return Path(out.stdout.strip())

    def flush_caches(self) -> None:
        """
        Disable flush, because it calls prefetch() which resets the overridden Flake._path
        """
        return


def parse_args() -> argparse.Namespace:
    import argparse

    parser = argparse.ArgumentParser(
        description="Update the vars of an inventory test",
    )
    parser.add_argument(
        "test_name",
        type=str,
        help="The name of the test to update",
    )
    return parser.parse_args()


if __name__ == "__main__":
    os.environ["CLAN_NO_COMMIT"] = "1"
    args = parse_args()
    test_dir = _test_dir(args.test_name)
    subprocess.run(["rm", "-rf", f"{test_dir}/vars", f"{test_dir}/sops"])
    flake = Flake(str(test_dir))
    flake._path = test_dir  # noqa SLF001
    flake._is_local = True  # noqa SLF001
    machines = [
        TestMachine(name, flake, args.test_name)
        for name in machine_names(args.test_name)
    ]
    user = "admin"
    admin_key_path = Path(flake.path / "sops" / "users" / user / "key.json")
    admin_key_path.parent.mkdir(parents=True, exist_ok=True)
    admin_key_path.write_text(
        json.dumps(
            {
                "publickey": sops_pub_key,
                "type": "age",
            }
        )
    )
    with NamedTemporaryFile("w") as f:
        f.write("# created: 2023-07-17T10:51:45+02:00\n")
        f.write(f"# public key: {sops_pub_key}\n")
        f.write(sops_priv_key)
        f.seek(0)
        print(Path(f.name).read_text())
        os.environ["SOPS_AGE_KEY_FILE"] = f.name
        generate_vars(list(machines))
