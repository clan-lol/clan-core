#! /usr/bin/env python3

import argparse
import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, override

from clan_lib.dirs import find_toplevel
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_eval, nix_test_store
from clan_lib.nix_models.typing import MachineInput
from clan_lib.vars.generate import run_generators
from clan_lib.vars.generator import Generator
from clan_lib.vars.prompt import PromptType

if TYPE_CHECKING:
    from clan_lib.machines.actions import (
        ListOptions,
        MachineResponse,
    )

log = logging.getLogger(__name__)

sops_priv_key = (
    "AGE-SECRET-KEY-1PL0M9CWRCG3PZ9DXRTTLMCVD57U6JDFE8K7DNVQ35F4JENZ6G3MQ0RQLRV"
)
sops_pub_key = "age1qm0p4vf9jvcnn43s6l4prk8zn6cx0ep9gzvevxecv729xz540v8qa742eg"


def get_machine_names(repo_root: Path, check_attr: str, system: str) -> list[str]:
    """Get the machine names from the test flake"""
    nix_options = []
    if tmp_store := nix_test_store():
        nix_options += ["--store", str(tmp_store)]
    cmd = nix_eval(
        [
            f"path://{repo_root}#checks.{system}.{check_attr}.nodes",
            "--apply",
            "builtins.attrNames",
            *nix_options,
        ],
    )
    out = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(out.stdout.strip())


class TestFlake(Flake):
    """Flake class which is able to deal with not having an actual flake.
    All nix build and eval calls will be forwarded to:
      clan-core#checks.<system>.<test_name>
    """

    def __init__(
        self, check_attr: str, test_dir: Path, *args: Any, **kwargs: Any
    ) -> None:
        """Initialize the TestFlake with the check attribute."""
        super().__init__(*args, **kwargs)
        self.check_attr = check_attr
        self.test_dir = test_dir

    @override
    def precache(self, selectors: list[str]) -> None:
        # Precaching is broken since 501d02056222216330b3820d1c252ffdc81b7daf
        # TODO @DavHau pls fix!
        pass

    @property
    def path(self) -> Path:
        return self.test_dir

    def machine_selector(self, machine_name: str, selector: str) -> str:
        """Create a selector for a specific machine.

        Args:
            machine_name: The name of the machine
            selector: The attribute selector string relative to the machine config
        Returns:
            The full selector string for the machine

        """
        config = nix_config()
        system = config["system"]
        test_system = system
        if system.endswith("-darwin"):
            test_system = system.rstrip("darwin") + "linux"
        return f'checks."{test_system}".{self.check_attr}.machinesCross."{system}"."{machine_name}".{selector}'

    # we don't want to evaluate all machines of the flake. Only the ones defined in the test
    def set_machine_names(self, machine_names: list[str]) -> None:
        """Set the machine names for this flake instance to fake the machines defined by the test"""
        self._machine_names = machine_names

    def list_machines(
        self,
        opts: "ListOptions | None" = None,  # noqa: ARG002
    ) -> "dict[str, MachineResponse]":
        """List machines of a clan"""
        from clan_lib.machines.actions import (  # noqa: PLC0415
            MachineResponse,
        )

        res = {}
        for name in self._machine_names:
            res[name] = MachineResponse(data=MachineInput(deploy={}))
        return res


class TestMachine(Machine):
    """Machine class which is able to deal with not having an actual flake.
    All nix build and eval calls will be forwarded to:
      clan-core#checks.<system>.<test_name>.nodes.<machine_name>.<attr>
    """

    @override
    def __init__(
        self,
        name: str,
        flake: Flake,
        test_dir: Path,
        check_attr: str,
    ) -> None:
        super().__init__(name, flake)
        self.check_attr = check_attr
        self.test_dir = test_dir

    @property
    def flake_dir(self) -> Path:
        return self.test_dir

    def select(self, attr: str) -> Any:
        """Build the machine and return the path to the result
        accepts a secret store and a public store
        """
        config = nix_config()
        system = config["system"]
        test_system = system
        if system.endswith("-darwin"):
            test_system = system.rstrip("darwin") + "linux"

        return self.flake.select(
            f'checks."{test_system}".{self.check_attr}.machinesCross.{system}.{self.name}.{attr}',
        )


@dataclass
class Options:
    repo_root: Path
    test_dir: Path
    check_attr: str
    clean: bool


def parse_args() -> Options:
    parser = argparse.ArgumentParser(
        description="""
            Update the vars of a 'clanTest' integration test.
            See 'clanLib.test.clanTest' for more information on how to create such a test.
        """,
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="""
            Should be an absolute path to the repo root.
            This path is used as root to evaluate and build attributes using the nix commands.
            i.e. 'nix eval <repo_root>#checks ...'
        """,
        required=False,
        default=os.environ.get("PRJ_ROOT", find_toplevel([".git"])),
    )
    parser.add_argument(
        "--clean",
        help="wipe vars and sops directories before generating new vars",
        action="store_true",
        default=False,
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
        clean=args.clean,
    )


def generate_test_vars(
    clean: bool,
    repo_root: Path,
    test_dir: Path,
    check_attr: str,
) -> None:
    if clean:
        shutil.rmtree(test_dir / "vars", ignore_errors=True)
        shutil.rmtree(test_dir / "sops", ignore_errors=True)

    config = nix_config()
    system = config["system"]
    test_system = system
    if system.endswith("-darwin"):
        test_system = system.rstrip("darwin") + "linux"

    flake = TestFlake(check_attr, test_dir, str(repo_root))
    machine_names = get_machine_names(
        repo_root,
        check_attr,
        test_system,
    )

    flake.set_machine_names(machine_names)

    flake.precache(
        [
            f"checks.{test_system}.{check_attr}.machinesCross.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
        ],
    )

    # This hack is necessary because the sops store uses flake.path to find the machine keys
    # This hack does not work because flake.invalidate_cache resets _path
    flake._path = test_dir  # noqa: SLF001

    machines = [
        TestMachine(name, flake, test_dir, check_attr) for name in machine_names
    ]
    user = "admin"
    admin_key_path = Path(test_dir.resolve() / "sops" / "users" / user / "key.json")
    admin_key_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ["SOPS_AGE_KEY_FILE"] = str(admin_key_path)
    admin_key_path.write_text(
        json.dumps(
            {
                "publickey": sops_pub_key,
                "type": "age",
            },
            indent=2,
        )
        + "\n",
    )

    def mocked_prompts(
        generator: Generator,
    ) -> dict[str, str]:
        prompt_values: dict[str, str] = {}
        for prompt in generator.prompts:
            var_id = f"{generator.name}/{prompt.name}"
            if prompt.prompt_type == PromptType.HIDDEN:
                prompt_values[prompt.name] = "fake_hidden_value"
            elif prompt.prompt_type == PromptType.MULTILINE_HIDDEN:
                prompt_values[prompt.name] = "fake\nmultiline\nhidden\nvalue"
            elif prompt.prompt_type == PromptType.MULTILINE:
                prompt_values[prompt.name] = "fake\nmultiline\nvalue"
            elif prompt.prompt_type == PromptType.LINE:
                prompt_values[prompt.name] = "fake_line_value"
            else:
                msg = f"Unknown prompt type {prompt.prompt_type} for prompt {var_id} in generator {generator.name}"
                raise ClanError(msg)
        return prompt_values

    with NamedTemporaryFile("w") as f:
        f.write("# created: 2023-07-17T10:51:45+02:00\n")
        f.write(f"# public key: {sops_pub_key}\n")
        f.write(sops_priv_key)
        f.seek(0)
        os.environ["SOPS_AGE_KEY_FILE"] = f.name
        run_generators(list(machines), prompt_values=mocked_prompts)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    os.environ["CLAN_NO_COMMIT"] = "1"
    args = parse_args()
    generate_test_vars(
        clean=args.clean,
        repo_root=args.repo_root,
        test_dir=args.repo_root / args.test_dir,
        check_attr=args.check_attr,
    )


if __name__ == "__main__":
    main()
