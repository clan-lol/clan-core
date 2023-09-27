import logging
import os
import queue
import select
import shlex
import subprocess
import threading
from uuid import UUID, uuid4


class CmdState:
    def __init__(self, proc: subprocess.Popen) -> None:
        global LOOP
        self.proc: subprocess.Popen = proc
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self.output: queue.SimpleQueue = queue.SimpleQueue()
        self.returncode: int | None = None
        self.done: bool = False


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

    def run(self) -> None:
        self.finished = True

    def run_cmd(self, cmd: list[str]) -> CmdState:
        cwd = os.getcwd()
        self.log.debug(f"Working directory: {cwd}")
        self.log.debug(f"Running command: {shlex.join(cmd)}")
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
           # shell=True,
            cwd=cwd,
        )
        self.procs.append(CmdState(p))
        p_state = self.procs[-1]

        while p.poll() is None:
            # Check if stderr is ready to be read from
            rlist, _, _ = select.select([p.stderr, p.stdout], [], [], 0)
            if p.stderr in rlist:
                line = p.stderr.readline()
                if line != "":
                    p_state.stderr.append(line.strip("\n"))
                    self.log.debug(f"stderr: {line}")
                    p_state.output.put(line)

            if p.stdout in rlist:
                line = p.stdout.readline()
                if line != "":
                    p_state.stdout.append(line.strip("\n"))
                    self.log.debug(f"stdout: {line}")
                    p_state.output.put(line)

        p_state.returncode = p.returncode
        p_state.output.put(None)
        p_state.done = True

        if p.returncode != 0:
            raise RuntimeError(f"Failed to run command: {shlex.join(cmd)}")

        self.log.debug("Successfully ran command")
        return p_state


class TaskPool:
    def __init__(self) -> None:
        self.lock: threading.RLock = threading.RLock()
        self.pool: dict[UUID, BaseTask] = {}

    def __getitem__(self, uuid: str | UUID) -> BaseTask:
        with self.lock:
            if type(uuid) is UUID:
                return self.pool[uuid]
            else:
                uuid = UUID(uuid)
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


def register_task(task: BaseTask, *kwargs) -> UUID:
    global POOL
    if not issubclass(task, BaseTask):
        raise TypeError("task must be a subclass of BaseTask")

    uuid = uuid4()

    inst_task = task(uuid, *kwargs)
    POOL[uuid] = inst_task
    inst_task.start()
    return uuid
