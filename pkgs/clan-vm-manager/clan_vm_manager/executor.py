import os
import signal
import sys
import traceback
from pathlib import Path
from typing import Any

import gi

gi.require_version("GdkPixbuf", "2.0")

import multiprocessing as mp
from collections.abc import Callable

OUT_FILE: Path | None = None
IN_FILE: Path | None = None


class MPProcess:
    def __init__(
        self, *, name: str, proc: mp.Process, out_file: Path, in_file: Path
    ) -> None:
        self.name = name
        self.proc = proc
        self.out_file = out_file
        self.in_file = in_file

    # Kill the new process and all its children by sending a SIGTERM signal to the process group
    def kill_group(self) -> None:
        pid = self.proc.pid
        assert pid is not None
        os.killpg(pid, signal.SIGTERM)


def _set_proc_name(name: str) -> None:
    import ctypes

    # Define the prctl function with the appropriate arguments and return type
    libc = ctypes.CDLL("libc.so.6")
    prctl = libc.prctl
    prctl.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
    ]
    prctl.restype = ctypes.c_int

    # Set the process name to "my_process"
    prctl(15, name.encode(), 0, 0, 0)


def _signal_handler(signum: int, frame: Any) -> None:
    signame = signal.strsignal(signum)
    print("Signal received:", signame)

    # Delete files
    if OUT_FILE is not None:
        OUT_FILE.unlink()
    if IN_FILE is not None:
        IN_FILE.unlink()

    # Restore the default handler
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    # Re-raise the signal
    os.kill(os.getpid(), signum)


def _init_proc(
    func: Callable,
    out_file: Path,
    in_file: Path,
    wait_stdin_connect: bool,
    proc_name: str,
    **kwargs: Any,
) -> None:
    # Set the global variables
    global OUT_FILE, IN_FILE
    OUT_FILE = out_file
    IN_FILE = in_file

    # Create a new process group
    os.setsid()

    # Open stdout and stderr
    out_fd = os.open(str(out_file), flags=os.O_RDWR | os.O_CREAT | os.O_TRUNC)
    os.dup2(out_fd, sys.stdout.fileno())
    os.dup2(out_fd, sys.stderr.fileno())

    # Print some information
    pid = os.getpid()
    gpid = os.getpgid(pid=pid)
    print(f"Started new process pid={pid} gpid={gpid}")

    # Register the signal handler for SIGINT
    signal.signal(signal.SIGTERM, _signal_handler)

    # Set the process name
    _set_proc_name(proc_name)

    # Open stdin
    flags = None
    if wait_stdin_connect:
        print(f"Waiting for stdin connection on file {in_file}", file=sys.stderr)
        flags = os.O_RDONLY
    else:
        flags = os.O_RDONLY | os.O_NONBLOCK
    in_fd = os.open(str(in_file), flags=flags)
    os.dup2(in_fd, sys.stdin.fileno())

    # Execute the main function
    print(f"Executing function {func.__name__} now", file=sys.stderr)
    try:
        func(**kwargs)
    except Exception:
        traceback.print_exc()
        pid = os.getpid()
        gpid = os.getpgid(pid=pid)
        print(f"Killing process group pid={pid} gpid={gpid}")
        os.killpg(gpid, signal.SIGTERM)


def spawn(
    *, wait_stdin_con: bool, log_path: Path, func: Callable, **kwargs: Any
) -> MPProcess:
    # Decouple the process from the parent
    if mp.get_start_method(allow_none=True) is None:
        mp.set_start_method(method="spawn")

    # Set names
    proc_name = f"MPExec:{func.__name__}"
    out_file = log_path / "out.log"
    in_file = log_path / "in.fifo"

    # Create stdin fifo
    if in_file.exists():
        in_file.unlink()
    os.mkfifo(in_file)

    # Start the process
    proc = mp.Process(
        target=_init_proc,
        args=(func, out_file, in_file, wait_stdin_con, proc_name),
        name=proc_name,
        kwargs=kwargs,
    )
    proc.start()

    # Print some information
    assert proc.pid is not None
    print(f"Started process '{proc_name}'")
    print(f"Arguments: {kwargs}")
    if wait_stdin_con:
        cmd = f"cat - > {in_file}"
        print(f"Connect to stdin with : {cmd}")
    cmd = f"tail -f {out_file}"
    print(f"Connect to stdout with: {cmd}")

    # Return the process
    mp_proc = MPProcess(
        name=proc_name,
        proc=proc,
        out_file=out_file,
        in_file=in_file,
    )
    return mp_proc
