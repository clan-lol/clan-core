import subprocess
from pathlib import Path

import pytest
from clan_lib.nix import nix_shell


# fixture for git_repo
@pytest.fixture
def git_repo(temp_dir: Path) -> Path:
    # initialize a git repository
    cmd = nix_shell(["git"], ["git", "init"])
    subprocess.run(cmd, cwd=temp_dir, check=True)
    # set user.name and user.email
    cmd = nix_shell(["git"], ["git", "config", "user.name", "test"])
    subprocess.run(cmd, cwd=temp_dir, check=True)
    cmd = nix_shell(["git"], ["git", "config", "user.email", "test@test.test"])
    subprocess.run(cmd, cwd=temp_dir, check=True)
    # return the path to the git repository
    return temp_dir
