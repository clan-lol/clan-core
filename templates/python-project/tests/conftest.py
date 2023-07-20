import subprocess

import pytest


# returns a temporary directory with a fake git repo
@pytest.fixture()
def git_repo_path(tmp_path):
    subprocess.run(["mkdir", ".git"], cwd=tmp_path)
    return tmp_path
