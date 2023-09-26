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
        self.proc: subprocess.Process = proc
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self.output_pipe: asyncio.Queue = asyncio.Queue()
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
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            cwd=cwd,
        )
        state = CmdState(process)
        self.procs.append(state)

        while process.poll() is None:
            # Check if stderr is ready to be read from
            rlist, _, _ = select.select([process.stderr, process.stdout], [], [], 0)
            if process.stderr in rlist:
                line = process.stderr.readline()
                if line != "":
                    state.stderr.append(line.strip('\n'))
                    state.output_pipe.put_nowait(line)
            if process.stdout in rlist:
                line = process.stdout.readline()
                if line != "":
                    state.stdout.append(line.strip('\n'))
                    state.output_pipe.put_nowait(line)

        state.returncode = process.returncode
        state.done = True

        if process.returncode != 0:
            raise RuntimeError(
                f"Failed to run command: {shlex.join(cmd)}"
            )

        self.log.debug("Successfully ran command")
        return state


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


    def __setitem__(self, uuid: UUID, vm: BaseTask) -> None:
        with self.lock:
            if uuid in self.pool:
                raise KeyError(f"VM with uuid {uuid} already exists")
            if type(uuid) is not UUID:
                raise TypeError("uuid must be of type UUID")
            self.pool[uuid] = vm


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
