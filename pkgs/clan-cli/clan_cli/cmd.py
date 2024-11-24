import contextlib
import logging
import math
import os
import select
import shlex
import signal
import subprocess
import time
import timeit
import weakref
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from enum import Enum
from pathlib import Path
from typing import IO, Any

from clan_cli.custom_logger import print_trace
from clan_cli.errors import ClanCmdError, ClanError, CmdOut, indent_command

cmdlog = logging.getLogger(__name__)


class ClanCmdTimeoutError(ClanError):
    timeout: float

    def __init__(
        self,
        msg: str | None = None,
        *,
        description: str | None = None,
        location: str | None = None,
        timeout: float,
    ) -> None:
        self.timeout = timeout
        super().__init__(msg, description=description, location=location)


class Log(Enum):
    STDERR = 1
    STDOUT = 2
    BOTH = 3
    NONE = 4


def handle_io(
    process: subprocess.Popen,
    log: Log,
    cmdlog: logging.Logger,
    prefix: str,
    *,
    input_bytes: bytes | None,
    stdout: IO[bytes] | None,
    stderr: IO[bytes] | None,
    timeout: float = math.inf,
) -> tuple[str, str]:
    rlist = [process.stdout, process.stderr]
    wlist = [process.stdin] if input_bytes is not None else []
    stdout_buf = b""
    stderr_buf = b""
    start = time.time()

    # Loop until no more data is available
    while len(rlist) != 0 or len(wlist) != 0:
        # Check if the command has timed out
        if time.time() - start > timeout:
            msg = f"Command timed out after {timeout} seconds"
            description = prefix
            raise ClanCmdTimeoutError(msg=msg, description=description, timeout=timeout)

        # Wait for data to be available
        readlist, writelist, _ = select.select(rlist, wlist, [], 0.1)
        if len(readlist) == 0 and len(writelist) == 0:
            if process.poll() is None:
                continue
            # Process has exited
            break

        # Function to handle file descriptors
        def handle_fd(fd: IO[Any] | None, readlist: list[IO[Any]]) -> bytes:
            if fd and fd in readlist:
                read = os.read(fd.fileno(), 4096)
                if len(read) != 0:
                    return read
                rlist.remove(fd)
            return b""

        #
        # Process stdout
        #
        ret = handle_fd(process.stdout, readlist)
        if ret and log in [Log.STDOUT, Log.BOTH]:
            lines = ret.decode("utf-8", "replace").rstrip("\n").split("\n")
            for line in lines:
                cmdlog.info(line, extra={"command_prefix": prefix})
        if ret and stdout:
            stdout.write(ret)
            stdout.flush()

        #
        # Process stderr
        #
        stdout_buf += ret
        ret = handle_fd(process.stderr, readlist)

        if ret and log in [Log.STDERR, Log.BOTH]:
            lines = ret.decode("utf-8", "replace").rstrip("\n").split("\n")
            for line in lines:
                cmdlog.error(line, extra={"command_prefix": prefix})
        if ret and stderr:
            stderr.write(ret)
            stderr.flush()
        stderr_buf += ret

        #
        # Process stdin
        #
        if process.stdin in writelist:
            if input_bytes:
                try:
                    assert process.stdin is not None
                    written = os.write(process.stdin.fileno(), input_bytes)
                except BrokenPipeError:
                    wlist.remove(process.stdin)
                else:
                    input_bytes = input_bytes[written:]
                    if len(input_bytes) == 0:
                        wlist.remove(process.stdin)
                    process.stdin.flush()
                    process.stdin.close()
            else:
                wlist.remove(process.stdin)
    return stdout_buf.decode("utf-8", "replace"), stderr_buf.decode("utf-8", "replace")


@contextmanager
def terminate_process_group(process: subprocess.Popen) -> Iterator[None]:
    try:
        process_group = os.getpgid(process.pid)
    except ProcessLookupError:
        return
    if process_group == os.getpgid(os.getpid()):
        msg = "Bug! Refusing to terminate the current process group"
        raise ClanError(msg)
    try:
        yield
    finally:
        try:
            os.killpg(process_group, signal.SIGTERM)
            try:
                with contextlib.suppress(subprocess.TimeoutExpired):
                    # give the process time to terminate
                    process.wait(3)
            finally:
                os.killpg(process_group, signal.SIGKILL)
        except ProcessLookupError:  # process already terminated
            pass


@contextmanager
def terminate_process(process: subprocess.Popen) -> Iterator[None]:
    try:
        yield
    finally:
        try:
            process.terminate()
            try:
                with contextlib.suppress(subprocess.TimeoutExpired):
                    # give the process time to terminate
                    process.wait(3)
            finally:
                process.kill()
        except ProcessLookupError:
            pass


class TimeTable:
    """
    This class is used to store the time taken by each command
    and print it at the end of the program if env CLAN_CLI_PERF=1 is set.
    """

    def __init__(self) -> None:
        self.table: dict[str, float] = {}
        weakref.finalize(self, self.table_print)

    def table_print(self) -> None:
        print("======== CMD TIMETABLE ========")

        # Sort the table by time in descending order
        sorted_table = sorted(
            self.table.items(), key=lambda item: item[1], reverse=True
        )

        for k, v in sorted_table:
            # Check if timedelta is greater than 1 second
            if v > 1:
                # Print in red
                print(f"\033[91mTook {v}s\033[0m for command: '{k}'")
            else:
                # Print in default color
                print(f"Took {v} for command: '{k}'")

    def add(self, cmd: str, time: float) -> None:
        if cmd in self.table:
            self.table[cmd] += time
        else:
            self.table[cmd] = time


TIME_TABLE = None
if os.environ.get("CLAN_CLI_PERF"):
    TIME_TABLE = TimeTable()


def run(
    cmd: list[str],
    *,
    input: bytes | None = None,  # noqa: A002
    stdout: IO[bytes] | None = None,
    stderr: IO[bytes] | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    log: Log = Log.STDERR,
    logger: logging.Logger = cmdlog,
    prefix: str | None = None,
    check: bool = True,
    error_msg: str | None = None,
    needs_user_terminal: bool = False,
    timeout: float = math.inf,
    shell: bool = False,
) -> CmdOut:
    if cwd is None:
        cwd = Path.cwd()

    if prefix is None:
        prefix = "localhost"

    if input:
        if any(not ch.isprintable() for ch in input.decode("ascii", "replace")):
            filtered_input = "<<binary_blob>>"
        else:
            filtered_input = input.decode("ascii", "replace")
        print_trace(
            f"$: echo '{filtered_input}' | {indent_command(cmd)}", logger, prefix
        )
    elif logger.isEnabledFor(logging.DEBUG):
        print_trace(f"$: {indent_command(cmd)}", logger, prefix)

    start = timeit.default_timer()
    with ExitStack() as stack:
        stdin = subprocess.PIPE if input is not None else None
        process = stack.enter_context(
            subprocess.Popen(
                cmd,
                cwd=str(cwd),
                env=env,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=not needs_user_terminal,
                shell=shell,
            )
        )

        if needs_user_terminal:
            # we didn't allocate a new session, so we can't terminate the process group
            stack.enter_context(terminate_process(process))
        else:
            stack.enter_context(terminate_process_group(process))

        stdout_buf, stderr_buf = handle_io(
            process,
            log,
            prefix=prefix,
            cmdlog=logger,
            timeout=timeout,
            input_bytes=input,
            stdout=stdout,
            stderr=stderr,
        )
        process.wait()

    global TIME_TABLE
    if TIME_TABLE:
        TIME_TABLE.add(shlex.join(cmd), timeit.default_timer() - start)

    # Wait for the subprocess to finish
    cmd_out = CmdOut(
        stdout=stdout_buf,
        stderr=stderr_buf,
        cwd=cwd,
        env=env,
        command_list=cmd,
        returncode=process.returncode,
        msg=error_msg,
    )

    if check and process.returncode != 0:
        raise ClanCmdError(cmd_out)

    return cmd_out


def run_no_stdout(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    log: Log = Log.STDERR,
    logger: logging.Logger = cmdlog,
    prefix: str | None = None,
    check: bool = True,
    error_msg: str | None = None,
    needs_user_terminal: bool = False,
    shell: bool = False,
) -> CmdOut:
    """
    Like run, but automatically suppresses stdout, if not in DEBUG log level.
    If in DEBUG log level the stdout of commands will be shown.
    """
    if cwd is None:
        cwd = Path.cwd()
    if logger.isEnabledFor(logging.DEBUG):
        return run(cmd, env=env, log=log, check=check, error_msg=error_msg)
    log = Log.NONE
    return run(
        cmd,
        env=env,
        log=log,
        check=check,
        prefix=prefix,
        error_msg=error_msg,
        needs_user_terminal=needs_user_terminal,
        shell=shell,
    )
