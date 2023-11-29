import logging
import os
import queue
import select
import shlex
import subprocess
import sys
import threading
import traceback
from collections.abc import Iterator
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar
from uuid import UUID, uuid4

from .custom_logger import ThreadFormatter, get_caller
from .deal import deal
from .errors import ClanError


class Command:
    def __init__(self, log: logging.Logger) -> None:
        self.log: logging.Logger = log
        self.p: subprocess.Popen | None = None
        self._output: queue.SimpleQueue = queue.SimpleQueue()
        self.returncode: int | None = None
        self.done: bool = False
        self.stdout: list[str] = []
        self.stderr: list[str] = []

    def close_queue(self) -> None:
        if self.p is not None:
            self.returncode = self.p.returncode
        self._output.put(None)
        self.done = True

    def run(
        self,
        cmd: list[str],
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        name: str = "command",
    ) -> None:
        self.running = True
        self.log.debug(f"Command: {shlex.join(cmd)}")
        self.log.debug(f"Caller: {get_caller()}")

        cwd_res = None
        if cwd is not None:
            if not cwd.exists():
                raise ClanError(f"Working directory {cwd} does not exist")
            if not cwd.is_dir():
                raise ClanError(f"Working directory {cwd} is not a directory")
            cwd_res = cwd.resolve()
            self.log.debug(f"Working directory: {cwd_res}")

        self.p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            cwd=cwd_res,
            env=env,
        )
        assert self.p.stdout is not None and self.p.stderr is not None
        os.set_blocking(self.p.stdout.fileno(), False)
        os.set_blocking(self.p.stderr.fileno(), False)

        while self.p.poll() is None:
            # Check if stderr is ready to be read from
            rlist, _, _ = select.select([self.p.stderr, self.p.stdout], [], [], 0)
            for fd in rlist:
                try:
                    for line in fd:
                        self.log.debug(f"[{name}] {line.rstrip()}")
                        if fd == self.p.stderr:
                            self.stderr.append(line)
                        else:
                            self.stdout.append(line)
                        self._output.put(line)
                except BlockingIOError:
                    continue

        if self.p.returncode != 0:
            raise ClanError(f"Failed to run command: {shlex.join(cmd)}")


class TaskStatus(str, Enum):
    NOTSTARTED = "NOTSTARTED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class BaseTask:
    def __init__(self, uuid: UUID, num_cmds: int) -> None:
        # constructor
        self.uuid: UUID = uuid
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(ThreadFormatter())
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        self.log = logger
        self.log = logger
        self.procs: list[Command] = []
        self.status = TaskStatus.NOTSTARTED
        self.logs_lock = threading.Lock()
        self.error: Exception | None = None

        for _ in range(num_cmds):
            cmd = Command(self.log)
            self.procs.append(cmd)

    def _run(self) -> None:
        self.status = TaskStatus.RUNNING
        try:
            self.run()
            # TODO: We need to check, if too many commands have been initialized,
            # but not run. This would deadlock the log_lines() function.
            # Idea: Run next(cmds) and check if it raises StopIteration if not,
            # we have too many commands
        except Exception as e:
            # FIXME: fix exception handling here
            traceback.print_exception(*sys.exc_info())
            self.error = e
            self.log.exception(e)
            self.status = TaskStatus.FAILED
        else:
            self.status = TaskStatus.FINISHED
        finally:
            for proc in self.procs:
                proc.close_queue()

    def run(self) -> None:
        raise NotImplementedError

    ## TODO: Test when two clients are connected to the same task
    def log_lines(self) -> Iterator[str]:
        with self.logs_lock:
            for proc in self.procs:
                if self.status == TaskStatus.FINISHED:
                    return
                # process has finished
                if proc.done:
                    for line in proc.stdout:
                        yield line
                    for line in proc.stderr:
                        yield line
                else:
                    while line := proc._output.get():
                        yield line

    def commands(self) -> Iterator[Command]:
        yield from self.procs


# TODO: We need to test concurrency
class TaskPool:
    def __init__(self) -> None:
        self.lock: threading.RLock = threading.RLock()
        self.pool: dict[UUID, BaseTask] = {}

    def __getitem__(self, uuid: UUID) -> BaseTask:
        with self.lock:
            if uuid not in self.pool:
                raise ClanError(f"Task with uuid {uuid} does not exist")
            return self.pool[uuid]

    def __setitem__(self, uuid: UUID, task: BaseTask) -> None:
        with self.lock:
            if uuid in self.pool:
                raise KeyError(f"Task with uuid {uuid} already exists")
            if type(uuid) is not UUID:
                raise TypeError("uuid must be of type UUID")
            self.pool[uuid] = task


POOL: TaskPool = TaskPool()


@deal.raises(ClanError)
def get_task(uuid: UUID) -> BaseTask:
    global POOL
    return POOL[uuid]


T = TypeVar("T", bound="BaseTask")


@deal.raises(ClanError)
def create_task(task_type: type[T], *args: Any) -> T:
    global POOL

    # check if task_type is a callable
    if not callable(task_type):
        raise ClanError("task_type must be callable")
    uuid = uuid4()

    task = task_type(uuid, *args)
    POOL[uuid] = task
    threading.Thread(target=task._run).start()
    return task
