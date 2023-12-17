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

    def kill_all(self) -> None:
        pid = self.proc.pid
        assert pid is not None

        # Get the process group ID of the new process
        new_pgid = os.getpgid(pid)
        # Kill the new process and all its children by sending a SIGTERM signal to the process group
        os.killpg(new_pgid, signal.SIGTERM)

    # def get_all_output(self) -> str:
    #     os.lseek(self.out_fd, 0, os.SEEK_SET)
    #     return os.read(self.out_fd, 1024).decode("utf-8")

    # def write_all_input(self, input_str: str) -> None:
    #     os.lseek(self.in_fd, 0, os.SEEK_SET)
    #     os.write(self.in_fd, input_str.encode("utf-8"))


def init_proc(
    func: Callable, out_file: str, in_file: str, wait_stdin_connect: bool, **kwargs: Any
) -> None:
    os.setsid()

    out_fd = os.open(out_file, flags=os.O_RDWR | os.O_CREAT | os.O_TRUNC)
    os.dup2(out_fd, sys.stdout.fileno())
    os.dup2(out_fd, sys.stderr.fileno())

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
        print("Setting start method to spawn")
        mp.set_start_method(method="spawn")
    # rand_name = str(uuid.uuid4())
    rand_name = "test"
    proc_name = f"MPExecutor:{func.__name__}:{rand_name}"
    out_file_name = f"{rand_name}_out.log"
    in_file_name = f"{rand_name}_in.log"

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
    print(f"Started process '{proc_name}'. pid={proc.pid} gpid={os.getpgid(proc.pid)}")

    mp_proc = MPProcess(
        name=proc_name,
        proc=proc,
        out_file_name=out_file_name,
        in_file_name=in_file_name,
    )
    return mp_proc
