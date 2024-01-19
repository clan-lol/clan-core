import shutil
from math import floor
from pathlib import Path


def get_term_filler(name: str) -> int:
    width, height = shutil.get_terminal_size()

    filler = floor((width - len(name)) / 2)
    return filler - 1


def text_heading(heading: str) -> str:
    filler = get_term_filler(heading)
    return f"{'=' * filler} {heading} {'=' * filler}"


class CmdOut:
    def __init__(
        self,
        stdout: str,
        stderr: str,
        cwd: Path,
        command: str,
        returncode: int,
        msg: str | None,
    ) -> None:
        super().__init__()
        self.stdout = stdout
        self.stderr = stderr
        self.cwd = cwd
        self.command = command
        self.returncode = returncode
        self.msg = msg

        self.error_str = f"""
{text_heading(heading="Command")}
{self.command}
{text_heading(heading="Stderr")}
{self.stderr}
{text_heading(heading="Stdout")}
{self.stdout}
{text_heading(heading="Metadata")}
Message: {self.msg}
Working Directory: '{self.cwd}'
Return Code: {self.returncode}
        """

    def __str__(self) -> str:
        return self.error_str


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

    def __str__(self) -> str:
        return str(self.cmd)

    def __repr__(self) -> str:
        return f"ClanCmdError({self.cmd})"
