import logging
import os
import pty
import select
import shlex
import subprocess
import sys
import weakref
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from .custom_logger import get_caller
from .errors import ClanCmdError, CmdOut

glog = logging.getLogger(__name__)


class Log(Enum):
    STDERR = 1
    STDOUT = 2
    BOTH = 3
    NONE = 4


class TimeTable:
    """
    This class is used to store the time taken by each command
    and print it at the end of the program if env PERF=1 is set.
    """

    def __init__(self) -> None:
        self.table: dict[str, timedelta] = {}
        weakref.finalize(self, self.table_print)

    def table_print(self) -> None:
        if os.getenv("PERF") != "1":
            return
        print("======== CMD TIMETABLE ========")

        # Sort the table by time in descending order
        sorted_table = sorted(
            self.table.items(), key=lambda item: item[1], reverse=True
        )

        for k, v in sorted_table:
            # Check if timedelta is greater than 1 second
            if v.total_seconds() > 1:
                # Print in red
                print(f"\033[91mTook {v}s\033[0m for command: '{k}'")
            else:
                # Print in default color
                print(f"Took {v} for command: '{k}'")

    def add(self, cmd: str, time: timedelta) -> None:
        if cmd in self.table:
            self.table[cmd] += time
        else:
            self.table[cmd] = time


TIME_TABLE = TimeTable()


def run(
    cmd: list[str],
    *,
    input: bytes | None = None,  # noqa: A002
    env: dict[str, str] | None = None,
    cwd: Path = Path.cwd(),
    log: Log = Log.STDERR,
    check: bool = True,
    error_msg: str | None = None,
) -> CmdOut:
    if input:
        glog.debug(
            f"""$: echo "{input.decode('utf-8', 'replace')}" | {shlex.join(cmd)} \nCaller: {get_caller()}"""
        )
    else:
        glog.debug(f"$: {shlex.join(cmd)} \nCaller: {get_caller()}")

    # Create pseudo-terminals for stdout/stderr and stdin
    stdout_master_fd, stdout_slave_fd = pty.openpty()
    stderr_master_fd, stderr_slave_fd = pty.openpty()

    tstart = datetime.now()

    proc = subprocess.Popen(
        cmd,
        preexec_fn=os.setsid,
        stdin=stdout_slave_fd,
        stdout=stdout_slave_fd,
        stderr=stderr_slave_fd,
        close_fds=True,
        env=env,
        cwd=str(cwd),
    )

    os.close(stdout_slave_fd)  # Close slave FD in parent
    os.close(stderr_slave_fd)  # Close slave FD in parent

    stdout_file = sys.stdout
    stderr_file = sys.stderr
    stdout_buf = b""
    stderr_buf = b""

    if input:
        written_b = os.write(stdout_master_fd, input)

        if written_b != len(input):
            raise ValueError("Could not write all input to subprocess")

    rlist = [stdout_master_fd, stderr_master_fd]

    def handle_fd(fd: int | None) -> bytes:
        if fd and fd in r:
            try:
                read = os.read(fd, 4096)
                if len(read) != 0:
                    return read
            except OSError:
                pass
            rlist.remove(fd)
        return b""

    while len(rlist) != 0:
        r, w, e = select.select(rlist, [], [], 0.1)
        if len(r) == 0:  # timeout in select
            if proc.poll() is None:
                continue
            # Process has exited
            break

        ret = handle_fd(stdout_master_fd)
        stdout_buf += ret
        if ret and log in [Log.STDOUT, Log.BOTH]:
            stdout_file.buffer.write(ret)
            stdout_file.flush()

        ret = handle_fd(stderr_master_fd)
        stderr_buf += ret
        if ret and log in [Log.STDERR, Log.BOTH]:
            stderr_file.buffer.write(ret)
            stderr_file.flush()

    os.close(stdout_master_fd)
    os.close(stderr_master_fd)

    proc.wait()

    tend = datetime.now()
    global TIME_TABLE
    TIME_TABLE.add(shlex.join(cmd), tend - tstart)

    # Wait for the subprocess to finish
    cmd_out = CmdOut(
        stdout=stdout_buf.decode("utf-8", "replace"),
        stderr=stderr_buf.decode("utf-8", "replace"),
        cwd=cwd,
        command=shlex.join(cmd),
        returncode=proc.returncode,
        msg=error_msg,
    )

    if check and proc.returncode != 0:
        raise ClanCmdError(cmd_out)

    return cmd_out


def run_no_stdout(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path = Path.cwd(),
    log: Log = Log.STDERR,
    check: bool = True,
    error_msg: str | None = None,
) -> CmdOut:
    """
    Like run, but automatically suppresses stdout, if not in DEBUG log level.
    If in DEBUG log level the stdout of commands will be shown.
    """
    if logging.getLogger(__name__.split(".")[0]).isEnabledFor(logging.DEBUG):
        return run(cmd, env=env, log=log, check=check, error_msg=error_msg)
    else:
        log = Log.NONE
        return run(cmd, env=env, log=log, check=check, error_msg=error_msg)
