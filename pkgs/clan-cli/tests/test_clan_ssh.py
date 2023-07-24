import argparse
import json
import tempfile
from typing import Union

import pytest_subprocess.fake_process
from pytest_subprocess import utils

import clan_cli.ssh


# using fp fixture from pytest-subprocess
def test_ssh_no_pass(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    host = "somehost"
    user = "user"
    cmd: list[Union[str, utils.Any]] = [
        "torify",
        "ssh",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
        f"{user}@{host}",
    ]
    fp.register(cmd)
    clan_cli.ssh.ssh(
        host=host,
        user=user,
    )
    assert fp.call_count(cmd) == 1


# using fp fixture from pytest-subprocess
def test_ssh_json(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    with tempfile.NamedTemporaryFile(mode="w+") as file:
        json.dump({"password": "XXX", "address": "somehost"}, file)
        cmd: list[Union[str, utils.Any]] = [
            "nix",
            "shell",
            "nixpkgs#sshpass",
            "-c",
            "torify",
            "sshpass",
            "-p",
            "XXX",
            "ssh",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            "root@somehost",
        ]
        fp.register(cmd)
        file.seek(0)  # write file and go to the beginning
        args = argparse.Namespace(json=file.name, ssh_args=[])
        clan_cli.ssh.main(args)
        assert fp.call_count(cmd) == 1
