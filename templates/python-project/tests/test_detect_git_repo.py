import tempfile

import my_lib


# using the fixture from conftest.py
def test_is_git_repo(git_repo_path: str) -> None:
    result = my_lib.detect_git_repo(git_repo_path)
    assert result is True


# using the fixture from conftest.py
def test_is_not_git_repo() -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        result = my_lib.detect_git_repo(tempdir)
    assert result is False
