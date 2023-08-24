from typing import Union

import pytest_subprocess.fake_process
from cli import Cli
from pytest_subprocess import utils


# using fp fixture from pytest-subprocess
def test_create(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    cmd: list[Union[str, utils.Any]] = ["nix", "flake", "init", "-t", fp.any()]
    fp.register(cmd)
    cli = Cli()
    cli.run(["admin", "--folder", "./my-clan", "create"])
    assert fp.call_count(cmd) == 1
