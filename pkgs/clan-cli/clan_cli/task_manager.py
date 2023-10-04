import logging
import os
import queue
import select
import shlex
import subprocess
import sys
import threading
import traceback
from enum import Enum
from typing import Any, Iterator, Type, TypeVar
from uuid import UUID, uuid4

from .errors import ClanError


class Command:
    def __init__(self, log: logging.Logger) -> None:
        self.log: logging.Logger = log
        self.p: subprocess.Popen | None = None
        self._output: queue.SimpleQueue = queue.SimpleQueue()
        self.returncode: int | None = None
        self.done: bool = False
        self.lines: list[str] = []

    def close_queue(self) -> None:
        if self.p is not None:
            self.returncode = self.p.returncode
        self._output.put(None)
        self.done = True

    def run(self, cmd: list[str]) -> None:
        self.running = True
        try:
            self.log.debug(f"Running command: {shlex.join(cmd)}")
            self.p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
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
                            self.log.debug("stdout: %s", line)
                            self.lines.append(line)
                            self._output.put(line)
                    except BlockingIOError:
                        continue

            if self.p.returncode != 0:
                raise ClanError(f"Failed to run command: {shlex.join(cmd)}")

            self.log.debug("Successfully ran command")
        finally:
            self.close_queue()


class TaskStatus(str, Enum):
    NOTSTARTED = "NOTSTARTED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class BaseTask:
    def __init__(self, uuid: UUID) -> None:
        # constructor
        self.uuid: UUID = uuid
        self.log = logging.getLogger(__name__)
        self.procs: list[Command] = []
        self.status = TaskStatus.NOTSTARTED
        self.logs_lock = threading.Lock()
        self.error: Exception | None = None

    def _run(self) -> None:
        self.status = TaskStatus.RUNNING
        try:
            self.run()
        except Exception as e:
            # FIXME: fix exception handling here
            traceback.print_exception(*sys.exc_info())
            for proc in self.procs:
                proc.close_queue()
            self.error = e
            self.log.exception(e)
            self.status = TaskStatus.FAILED
        else:
            self.status = TaskStatus.FINISHED

    def run(self) -> None:
        raise NotImplementedError

    ## TODO: If two clients are connected to the same task,
    def log_lines(self) -> Iterator[str]:
        with self.logs_lock:
            for proc in self.procs:
                if self.status == TaskStatus.FINISHED:
                    return
                # process has finished
                if proc.done:
                    for line in proc.lines:
                        yield line
                else:
                    while line := proc._output.get():
                        yield line

    def register_commands(self, num_cmds: int) -> Iterator[Command]:
        for _ in range(num_cmds):
            cmd = Command(self.log)
            self.procs.append(cmd)

        for cmd in self.procs:
            yield cmd


# TODO: We need to test concurrency
class TaskPool:
    def __init__(self) -> None:
        self.lock: threading.RLock = threading.RLock()
        self.pool: dict[UUID, BaseTask] = {}

    def __getitem__(self, uuid: UUID) -> BaseTask:
        with self.lock:
            return self.pool[uuid]

    def __setitem__(self, uuid: UUID, task: BaseTask) -> None:
        with self.lock:
            if uuid in self.pool:
                raise KeyError(f"Task with uuid {uuid} already exists")
            if type(uuid) is not UUID:
                raise TypeError("uuid must be of type UUID")
            self.pool[uuid] = task


POOL: TaskPool = TaskPool()


def get_task(uuid: UUID) -> BaseTask:
    global POOL
    return POOL[uuid]


T = TypeVar("T", bound="BaseTask")


def create_task(task_type: Type[T], *args: Any) -> T:
    global POOL

    uuid = uuid4()

    task = task_type(uuid, *args)
    threading.Thread(target=task._run).start()
    POOL[uuid] = task
    return task
