#! /usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, override

from clan_cli.machines.machines import Machine
from clan_cli.vars.generate import generate_vars
from clan_lib.dirs import find_git_repo_root
from clan_lib.flake.flake import Flake
from clan_lib.nix import nix_config, nix_eval

sops_priv_key = (
    "AGE-SECRET-KEY-1PL0M9CWRCG3PZ9DXRTTLMCVD57U6JDFE8K7DNVQ35F4JENZ6G3MQ0RQLRV"
)
sops_pub_key = "age1qm0p4vf9jvcnn43s6l4prk8zn6cx0ep9gzvevxecv729xz540v8qa742eg"


def get_machine_names(repo_root: Path, check_attr: str) -> list[str]:
    """
    Get the machine names from the test flake
    """
    cmd = nix_eval(
        [
            f"git+file://{repo_root}#checks.{nix_config()['system']}.{check_attr}.nodes",
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

    @override
    def __init__(
        self, name: str, flake: Flake, test_dir: Path, check_attr: str
    ) -> None:
        super().__init__(name, flake)
        self.check_attr = check_attr
        self.test_dir = test_dir

    @property
    def flake_dir(self) -> Path:
        return self.test_dir

    @override
    def nix(
        self,
        attr: str,
        nix_options: list[str] | None = None,
    ) -> Any:
        """
        Build the machine and return the path to the result
        accepts a secret store and a facts store # TODO
        """
        if nix_options is None:
            nix_options = []

        config = nix_config()
        system = config["system"]

        return self.flake.select(
            f'checks."{system}".{self.check_attr}.nodes.{self.name}.{attr}',
            nix_options=nix_options,
        )


@dataclass
class Options:
    repo_root: Path
    test_dir: Path
    check_attr: str


def parse_args() -> Options:
    parser = argparse.ArgumentParser(
        description="""
            Update the vars of a 'makeTestClan' integration test.
            See 'clanLib.test.makeTestClan' for more information on how to create such a test.
        """,
    )
    parser.add_argument(
        "--repo_root",
        type=Path,
        help="""
            Should be an absolute path to the repo root.
            This path is used as root to evaluate and build attributes using the nix commands.
            i.e. 'nix eval <repo_root>#checks ...'
        """,
        required=False,
        default=os.environ.get("PRJ_ROOT", find_git_repo_root()),
    )
    parser.add_argument(
        "test_dir",
        type=Path,
        help="""
            The folder of the test. Usually passed as 'directory' to clan in the test.
            Must be relative to the repo_root.
        """,
    )
    parser.add_argument(
        "check_attr",
        type=str,
        help="The attribute name of the flake#checks to update",
    )
    args = parser.parse_args()
    return Options(
        repo_root=args.repo_root,
        test_dir=args.test_dir,
        check_attr=args.check_attr,
    )


def main() -> None:
    os.environ["CLAN_NO_COMMIT"] = "1"
    opts = parse_args()
    test_dir = opts.repo_root / opts.test_dir

    shutil.rmtree(test_dir / "vars", ignore_errors=True)
    shutil.rmtree(test_dir / "sops", ignore_errors=True)

    flake = Flake(str(opts.repo_root))
    machine_names = get_machine_names(
        opts.repo_root,
        opts.check_attr,
    )

    config = nix_config()
    system = config["system"]
    flake.precache(
        [
            f"checks.{system}.{opts.check_attr}.nodes.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
            f"checks.{system}.{opts.check_attr}.nodes.{{{','.join(machine_names)}}}.config.system.clan.deployment.file",
        ]
    )

    machines = [
        TestMachine(name, flake, test_dir, opts.check_attr) for name in machine_names
    ]
    user = "admin"
    admin_key_path = Path(test_dir.resolve() / "sops" / "users" / user / "key.json")
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
        os.environ["SOPS_AGE_KEY_FILE"] = f.name
        generate_vars(list(machines))


if __name__ == "__main__":
    main()
