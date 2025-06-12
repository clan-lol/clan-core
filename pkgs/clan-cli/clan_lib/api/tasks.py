from clan_lib.api import API


@API.register_abstract
def cancel_task(task_id: str) -> None:
    """Cancel a task by its op_key."""
    msg = "cancel_task() is not implemented"
    raise NotImplementedError(msg)


@API.register_abstract
def list_tasks() -> list[str]:
    """List all tasks."""
    msg = "list_tasks() is not implemented"
    raise NotImplementedError(msg)
