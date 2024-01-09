import logging
import os
import select
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import IO, Any, NamedTuple

from .errors import ClanError

log = logging.getLogger(__name__)


class CmdOut(NamedTuple):
    stdout: str
    stderr: str
    cwd: Path | None = None


def handle_output(process: subprocess.Popen) -> tuple[str, str]:
    rlist = [process.stdout, process.stderr]
    stdout_buf = b""
    stderr_buf = b""

    while len(rlist) != 0:
        r, _, _ = select.select(rlist, [], [], 0)

        def handle_fd(fd: IO[Any] | None) -> bytes:
            if fd and fd in r:
                read = os.read(fd.fileno(), 4096)
                if len(read) != 0:
                    return read
                rlist.remove(fd)
            return b""

        ret = handle_fd(process.stdout)
        sys.stdout.buffer.write(ret)
        stdout_buf += ret
        ret = handle_fd(process.stderr)
        sys.stderr.buffer.write(ret)
        stderr_buf += ret
    return stdout_buf.decode("utf-8"), stderr_buf.decode("utf-8")


def run(cmd: list[str], cwd: Path = Path.cwd()) -> CmdOut:
    # Start the subprocess
    process = subprocess.Popen(
        cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    stdout_buf, stderr_buf = handle_output(process)

    # Wait for the subprocess to finish
    rc = process.wait()

    if rc != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
working directory: {cwd}
exit code: {rc}
stderr:
{stderr_buf}
stdout:
{stdout_buf}
"""
        )

    return CmdOut(stdout_buf, stderr_buf, cwd=cwd)


def runforcli(func: Callable[..., dict[str, CmdOut]], *args: Any) -> None:
    try:
        res = func(*args)

        for name, out in res.items():
            if out.stderr:
                print(f"{name}: {out.stderr}", end="")
            if out.stdout:
                print(f"{name}: {out.stdout}", end="")
    except ClanError as e:
        print(e)
        exit(1)
