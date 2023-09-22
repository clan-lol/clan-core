import subprocess
from pathlib import Path
from typing import Optional

from clan_cli.dirs import find_git_repo_root
from clan_cli.errors import ClanError
from clan_cli.nix import nix_shell


# generic vcs agnostic commit function
def commit_file(
    file_path: Path,
    repo_dir: Optional[Path] = None,
    commit_message: Optional[str] = None,
) -> None:
    # set default for repo_dir
    if repo_dir is None:
        repo_dir = find_git_repo_root()
    # check that the file is in the git repository and exists
    if not Path(file_path).resolve().is_relative_to(repo_dir.resolve()):
        raise ClanError(f"File {file_path} is not in the git repository {repo_dir}")
    if not file_path.exists():
        raise ClanError(f"File {file_path} does not exist")
    # generate commit message if not provided
    if commit_message is None:
        # ensure that mentioned file path is relative to repo
        commit_message = f"Add {file_path.relative_to(repo_dir)}"
    # check if the repo is a git repo and commit
    if (repo_dir / ".git").exists():
        _commit_file_to_git(repo_dir, file_path, commit_message)
    else:
        return


def _commit_file_to_git(repo_dir: Path, file_path: Path, commit_message: str) -> None:
    """Commit a file to a git repository.

    :param repo_dir: The path to the git repository.
    :param file_path: The path to the file to commit.
    :param commit_message: The commit message.
    :raises ClanError: If the file is not in the git repository.
    """
    # add the file to the git index
    subprocess.run(["git", "add", file_path], cwd=repo_dir, check=True)
    # commit only that file
    cmd = nix_shell(
        ["git"],
        ["git", "commit", "-m", commit_message, str(file_path.relative_to(repo_dir))],
    )
    subprocess.run(
        cmd,
        cwd=repo_dir,
        check=True,
    )
