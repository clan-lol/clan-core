import logging
import os
import queue
import select
import shlex
import subprocess
import threading
from typing import Any, Iterator
from uuid import UUID, uuid4


class CmdState:
    def __init__(self, log: logging.Logger) -> None:
        self.log: logging.Logger = log
        self.p: subprocess.Popen | None = None
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self._output: queue.SimpleQueue = queue.SimpleQueue()
        self.returncode: int | None = None
        self.done: bool = False
        self.running: bool = False
        self.cmd_str: str | None = None
        self.workdir: str | None = None

    def close_queue(self) -> None:
        if self.p is not None:
            self.returncode = self.p.returncode
        self._output.put(None)
        self.running = False
        self.done = True

    def run(self, cmd: list[str]) -> None:
        self.running = True
        try:
            self.cmd_str = shlex.join(cmd)
            self.workdir = os.getcwd()
            self.log.debug(f"Working directory: {self.workdir}")
            self.log.debug(f"Running command: {shlex.join(cmd)}")
            self.p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                cwd=self.workdir,
            )

            while self.p.poll() is None:
                # Check if stderr is ready to be read from
                rlist, _, _ = select.select([self.p.stderr, self.p.stdout], [], [], 0)
                if self.p.stderr in rlist:
                    assert self.p.stderr is not None
                    line = self.p.stderr.readline()
                    if line != "":
                        line = line.strip("\n")
                        self.stderr.append(line)
                        self.log.debug("stderr: %s", line)
                        self._output.put(line + '\n')

                if self.p.stdout in rlist:
                    assert self.p.stdout is not None
                    line = self.p.stdout.readline()
                    if line != "":
                        line = line.strip("\n")
                        self.stdout.append(line)
                        self.log.debug("stdout: %s", line)
                        self._output.put(line + '\n')

            if self.p.returncode != 0:
                raise RuntimeError(f"Failed to run command: {shlex.join(cmd)}")

            self.log.debug("Successfully ran command")
        finally:
            self.close_queue()


class BaseTask(threading.Thread):
    def __init__(self, uuid: UUID) -> None:
        # calling parent class constructor
        threading.Thread.__init__(self)

        # constructor
        self.uuid: UUID = uuid
        self.log = logging.getLogger(__name__)
        self.procs: list[CmdState] = []
        self.failed: bool = False
        self.finished: bool = False
        self.logs_lock = threading.Lock()

    def run(self) -> None:
        try:
            self.task_run()
        except Exception as e:
            for proc in self.procs:
                proc.close_queue()
            self.failed = True
            self.log.exception(e)
        finally:
            self.finished = True

    def task_run(self) -> None:
        raise NotImplementedError

    ## TODO: If two clients are connected to the same task,
    def logs_iter(self) -> Iterator[str]:
        with self.logs_lock:
            for proc in self.procs:
                if self.finished:
                    self.log.debug("log iter: Task is finished")
                    break
                if proc.done:
                    for line in proc.stderr:
                        yield line + '\n'
                    for line in proc.stdout:
                        yield line + '\n'
                    continue
                while True:
                    out = proc._output
                    line = out.get()
                    if line is None:
                        break
                    yield line

    def register_cmds(self, num_cmds: int) -> Iterator[CmdState]:
        for i in range(num_cmds):
            cmd = CmdState(self.log)
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


def register_task(task: type, *args: Any) -> UUID:
    global POOL
    if not issubclass(task, BaseTask):
        raise TypeError("task must be a subclass of BaseTask")

    uuid = uuid4()

    inst_task = task(uuid, *args)
    POOL[uuid] = inst_task
    inst_task.start()
    return uuid
