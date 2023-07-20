import os


def detect_git_repo(path: str) -> bool:
    return os.path.exists(f"{path}/.git")
