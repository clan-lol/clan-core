from pathlib import Path
from typing import NamedTuple


class CmdOut(NamedTuple):
    stdout: str
    stderr: str
    cwd: Path
    command: str
    returncode: int


class ClanError(Exception):
    """Base class for exceptions in this module."""

    pass


class ClanHttpError(ClanError):
    status_code: int
    msg: str

    def __init__(self, status_code: int, msg: str) -> None:
        self.status_code = status_code
        self.msg = msg
        super().__init__(msg)


class ClanCmdError(ClanError):
    cmd: CmdOut

    def __init__(self, cmd: CmdOut) -> None:
        self.cmd = cmd
        super().__init__()
