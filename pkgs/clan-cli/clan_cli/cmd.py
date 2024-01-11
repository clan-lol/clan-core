import logging
import os
import select
import shlex
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import IO, Any

from .custom_logger import get_caller
from .errors import ClanCmdError, CmdOut

glog = logging.getLogger(__name__)


class Log(Enum):
    STDERR = 1
    STDOUT = 2
    BOTH = 3


def handle_output(process: subprocess.Popen, log: Log) -> tuple[str, str]:
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
        if log in [Log.STDOUT, Log.BOTH]:
            sys.stdout.buffer.write(ret)
            sys.stdout.flush()

        stdout_buf += ret
        ret = handle_fd(process.stderr)

        if log in [Log.STDERR, Log.BOTH]:
            sys.stderr.buffer.write(ret)
            sys.stderr.flush()
        stderr_buf += ret
    return stdout_buf.decode("utf-8"), stderr_buf.decode("utf-8")


def run(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path = Path.cwd(),
    log: Log = Log.STDERR,
    check: bool = True,
    error_msg: str | None = None,
) -> CmdOut:
    glog.debug(f"running command: {shlex.join(cmd)}. Caller: {get_caller()}")
    # Start the subprocess
    process = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout_buf, stderr_buf = handle_output(process, log)

    # Wait for the subprocess to finish
    rc = process.wait()
    cmd_out = CmdOut(
        stdout=stdout_buf,
        stderr=stderr_buf,
        cwd=cwd,
        command=shlex.join(cmd),
        returncode=process.returncode,
        msg=error_msg,
    )

    if check and rc != 0:
        raise ClanCmdError(cmd_out)

    return cmd_out
