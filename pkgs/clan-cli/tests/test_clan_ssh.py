import os
import sys
from contextlib import contextmanager
from typing import Iterator, Union

import pytest
import pytest_subprocess.fake_process
from pytest_subprocess import utils

import clan_cli.ssh


def test_no_args(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["", "ssh"])
    with pytest.raises(SystemExit):
        clan_cli.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage:")


@contextmanager
def mock_env(**environ: str) -> Iterator[None]:
    original_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original_environ)


# using fp fixture from pytest-subprocess
def test_ssh_no_pass(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    with mock_env(CLAN_NIXPKGS="/mocked-nixpkgs"):
        host = "somehost"
        user = "user"
        cmd: list[Union[str, utils.Any]] = [
            "nix",
            "shell",
            "path:/mocked-nixpkgs#tor",
            "path:/mocked-nixpkgs#openssh",
            "-c",
            "torify",
            "ssh",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            f"{user}@{host}",
            fp.any(),
        ]
        fp.register(cmd)
        clan_cli.ssh.ssh(
            host=host,
            user=user,
        )
        assert fp.call_count(cmd) == 1


def test_ssh_with_pass(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    with mock_env(CLAN_NIXPKGS="/mocked-nixpkgs"):
        host = "somehost"
        user = "user"
        cmd: list[Union[str, utils.Any]] = [
            "nix",
            "shell",
            "path:/mocked-nixpkgs#tor",
            "path:/mocked-nixpkgs#openssh",
            "path:/mocked-nixpkgs#sshpass",
            "-c",
            "torify",
            "sshpass",
            "-p",
            fp.any(),
        ]
        fp.register(cmd)
        clan_cli.ssh.ssh(
            host=host,
            user=user,
            password="XXX",
        )
        assert fp.call_count(cmd) == 1


def test_qrcode_scan(fp: pytest_subprocess.fake_process.FakeProcess) -> None:
    cmd: list[Union[str, utils.Any]] = [fp.any()]
    fp.register(cmd, stdout="https://test.test")
    result = clan_cli.ssh.qrcode_scan("test.png")
    assert result == "https://test.test"
