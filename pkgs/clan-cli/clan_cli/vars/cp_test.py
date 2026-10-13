import shutil
import subprocess
from pathlib import Path

import pytest
from clan_cli.tests.age_keys import KeyPair
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.public_modules import in_repo as in_repo_mod
from clan_cli.vars.secret_modules import sops
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.machines.machines import Machine
from clan_lib.nix import run
from clan_lib.vars._types import GeneratorId, PerMachine, Shared
from clan_lib.vars.export_vars import export_vars
from clan_lib.vars.generator import (
    Generator,
)
from clan_lib.vars.import_vars import import_vars
from clan_lib.vars.list import get_machine_vars
from clan_lib.vars.secret_modules import age, password_store
from clan_lib.vars.set import set_var


def test_cp_command_no_flake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["vars", "cp", "machine1", "machine2", "var1"])


# adapted from test_vars_shared
@pytest.mark.broken_on_darwin  # idk, probably?
@pytest.mark.with_core
def test_cp_command_simple(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that copying a var from one machine to another results in the same var value"""
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    generator = machine1_config["clan"]["core"]["vars"]["generators"]["generator"]
    generator["files"]["my_value"]["secret"] = False
    generator["script"] = 'echo "$RANDOM" > "$out"/my_value'

    # machine 2 is equivalent to machine 1
    flake.machines["machine2"] = machine1_config

    flake.refresh()
    monkeypatch.chdir(flake.path)
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    machine2 = Machine(name="machine2", flake=Flake(str(flake.path)))
    in_repo_store_1 = in_repo_mod.VarsStore(machine1.flake)
    in_repo_store_2 = in_repo_mod.VarsStore(machine2.flake)
    # Create generators with machine context for testing
    gen_m1 = Generator(
        _flake=machine1.flake,
        key=GeneratorId(name="generator", placement=PerMachine("machine1")),
    )
    gen_m2 = Generator(
        _flake=machine2.flake,
        key=GeneratorId(name="generator", placement=PerMachine("machine2")),
    )
    cli.run(["vars", "generate", "--flake", str(flake.path)])
    # generate for machine 1
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    # copy from machine 1 to machine 2
    cli.run(
        [
            "vars",
            "cp",
            "--flake",
            str(flake.path),
            "machine1",
            "machine2",
            "generator/my_value",
        ]
    )
    # child value should be the same on both machines
    assert in_repo_store_1.get(gen_m1.key, "my_value") == in_repo_store_2.get(
        gen_m2.key, "my_value"
    ), "Child values should be the same after copying"


@pytest.mark.broken_on_darwin  # idk, probably?
@pytest.mark.with_core
def test_cp_command_fails_if_dest_does_not_have_generator(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that copying a var from one machine to another fails it the destination machine does not have the generator."""
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    generator = machine1_config["clan"]["core"]["vars"]["generators"]["generator"]
    generator["files"]["my_value"]["secret"] = False
    generator["script"] = 'echo "$RANDOM" > "$out"/my_value'

    # machine 2 initialized without the generator
    flake.machines["machine2"] = create_test_machine_config()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    cli.run(["vars", "generate", "--flake", str(flake.path)])
    # generate for machine 1
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])

    with pytest.raises(ClanError):
        # copy from machine 1 to machine 2
        cli.run(
            [
                "vars",
                "cp",
                "--flake",
                str(flake.path),
                "machine1",
                "machine2",
                "generator/my_value",
            ]
        )
