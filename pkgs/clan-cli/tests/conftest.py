import os
import subprocess
import sys
from pathlib import Path

import pytest

from clan_cli.nix import nix_shell

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

pytest_plugins = [
    "temporary_dir",
    "root",
    "age_keys",
    "sshd",
    "command",
    "ports",
    "host_group",
    "fixtures_flakes",
]


# fixture for git_repo
@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    # initialize a git repository
    cmd = nix_shell(["nixpkgs#git"], ["git", "init"])
    subprocess.run(cmd, cwd=tmp_path, check=True)
    # set user.name and user.email
    cmd = nix_shell(["nixpkgs#git"], ["git", "config", "user.name", "test"])
    subprocess.run(cmd, cwd=tmp_path, check=True)
    cmd = nix_shell(["nixpkgs#git"], ["git", "config", "user.email", "test@test.test"])
    subprocess.run(cmd, cwd=tmp_path, check=True)
    # return the path to the git repository
    return tmp_path
