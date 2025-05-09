import logging

from clan_lib.api import ErrorDataClass, SuccessDataClass

log = logging.getLogger(__name__)


def cancel_task(
    task_id: str, *, op_key: str
) -> SuccessDataClass[None] | ErrorDataClass:
    """Cancel a task by its op_key."""
    log.info(f"Cancelling task with op_key: {task_id}")
    return SuccessDataClass(
        op_key=op_key,
        data=None,
        status="success",
    )
