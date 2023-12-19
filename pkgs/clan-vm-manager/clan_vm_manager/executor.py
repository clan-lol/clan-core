import os
import signal
import sys
import traceback
from typing import Any

import gi

gi.require_version("GdkPixbuf", "2.0")

import multiprocessing as mp
from collections.abc import Callable


class MPProcess:
    def __init__(
        self, *, name: str, proc: mp.Process, out_file_name: str, in_file_name: str
    ) -> None:
        self.name = name
        self.proc = proc
        self.out_file_name = out_file_name
        self.in_file_name = in_file_name

    # Kill the new process and all its children by sending a SIGTERM signal to the process group
    def kill_group(self) -> None:
        pid = self.proc.pid
        assert pid is not None
        os.killpg(pid, signal.SIGTERM)


def signal_handler(signum: int, frame: Any) -> None:
    signame = signal.strsignal(signum)
    print("Signal received:", signame)

    # Restore the default handler
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    # Re-raise the signal
    os.kill(os.getpid(), signum)


def init_proc(
    func: Callable, out_file: str, in_file: str, wait_stdin_connect: bool, **kwargs: Any
) -> None:
    os.setsid()

    out_fd = os.open(out_file, flags=os.O_RDWR | os.O_CREAT | os.O_TRUNC)
    os.dup2(out_fd, sys.stdout.fileno())
    os.dup2(out_fd, sys.stderr.fileno())

    pid = os.getpid()
    gpid = os.getpgid(pid=pid)
    print(f"Started new process pid={pid} gpid={gpid}")

    # Register the signal handler for SIGINT
    signal.signal(signal.SIGTERM, signal_handler)

    flags = None
    if wait_stdin_connect:
        print(f"Waiting for stdin connection on file {in_file}", file=sys.stderr)
        flags = os.O_RDONLY
    else:
        flags = os.O_RDONLY | os.O_NONBLOCK

    in_fd = os.open(in_file, flags=flags)
    os.dup2(in_fd, sys.stdin.fileno())

    print(f"Executing function {func.__name__} now", file=sys.stderr)
    try:
        func(**kwargs)
    except Exception:
        traceback.print_exc()
        pid = os.getpid()
        gpid = os.getpgid(pid=pid)
        print(f"Killing process group pid={pid} gpid={gpid}")
        os.killpg(gpid, signal.SIGKILL)


def spawn(*, wait_stdin_connect: bool, func: Callable, **kwargs: Any) -> MPProcess:
    if mp.get_start_method(allow_none=True) is None:
        mp.set_start_method(method="spawn")
    # rand_name = str(uuid.uuid4())
    rand_name = "test"
    proc_name = f"MPExecutor:{rand_name}:{func.__name__}"
    out_file_name = f"{rand_name}_out.txt"
    in_file_name = f"{rand_name}_in.fifo"

    if os.path.exists(in_file_name):
        os.unlink(in_file_name)
    os.mkfifo(in_file_name)

    proc = mp.Process(
        target=init_proc,
        args=(func, out_file_name, in_file_name, wait_stdin_connect),
        name=proc_name,
        kwargs=kwargs,
    )
    proc.start()
    assert proc.pid is not None
    print(f"Started process '{proc_name}'")
    print(f"Arguments: {kwargs}")
    if wait_stdin_connect:
        cmd = f"cat - > {in_file_name}"
        print(f"Connect to stdin with : {cmd}")
    cmd = f"tail -f {out_file_name}"
    print(f"Connect to stdout with: {cmd}")
    mp_proc = MPProcess(
        name=proc_name,
        proc=proc,
        out_file_name=out_file_name,
        in_file_name=in_file_name,
    )
    return mp_proc
