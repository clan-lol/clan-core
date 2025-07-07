import logging
import threading
from dataclasses import dataclass

from clan_lib.api import API

log = logging.getLogger(__name__)


@dataclass
class WebThread:
    thread: threading.Thread
    stop_event: threading.Event


BAKEND_THREADS: dict[str, WebThread] | None = None


@API.register_abstract
def delete_task(task_id: str) -> None:
    """Cancel a task by its op_key."""
    assert BAKEND_THREADS is not None, "Backend threads not initialized"
    future = BAKEND_THREADS.get(task_id)
    if future:
        future.stop_event.set()
        log.debug(f"Task with id {task_id} has been cancelled.")
    else:
        msg = f"Task with id {task_id} not found."
        raise ValueError(msg)


@API.register
def list_tasks() -> list[str]:
    """List all tasks."""
    assert BAKEND_THREADS is not None, "Backend threads not initialized"
    return list(BAKEND_THREADS.keys())
