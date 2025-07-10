import logging
import threading
import time
from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.async_run import get_async_ctx, is_async_cancelled

log = logging.getLogger(__name__)


@dataclass
class WebThread:
    thread: threading.Thread
    stop_event: threading.Event


BAKEND_THREADS: dict[str, WebThread] | None = None


@API.register
def delete_task(task_id: str) -> None:
    """Cancel a task by its op_key."""
    assert BAKEND_THREADS is not None, "Backend threads not initialized"
    future = BAKEND_THREADS.get(task_id)

    log.debug(f"Thread ID: {threading.get_ident()}")
    if future:
        future.stop_event.set()
        log.debug(f"Task with id {task_id} has been cancelled.")
    else:
        msg = f"Task with id {task_id} not found."
        raise ValueError(msg)


@API.register
def run_task_blocking(somearg: str) -> str:
    """A long blocking task that simulates a long-running operation."""
    time.sleep(1)
    ctx = get_async_ctx()
    log.debug(f"Thread ID: {threading.get_ident()}")
    for i in range(30):
        if is_async_cancelled():
            log.debug("Task was cancelled")
            return "Task was cancelled"
        log.debug(
            f"Processing {i} for {somearg}. ctx.should_cancel={ctx.should_cancel()}"
        )
        time.sleep(1)
    return f"Task completed with argument: {somearg}"


@API.register
def list_tasks() -> list[str]:
    """List all tasks."""
    assert BAKEND_THREADS is not None, "Backend threads not initialized"
    return list(BAKEND_THREADS.keys())
