import argparse
from typing import Union

import pytest_subprocess.fake_process
from pytest_subprocess import utils

from clan_cli import admin


def test_make_parser() -> None:
    parser = argparse.ArgumentParser()
    admin.register_parser(parser)


# using fp fixture from pytest-subprocess
def test_create(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    cmd: list[Union[str, utils.Any]] = ["nix", "flake", "init", "-t", fp.any()]
    fp.register(cmd)
    args = argparse.Namespace(folder="./my-clan")
    admin.create(args)
    assert fp.call_count(cmd) == 1
