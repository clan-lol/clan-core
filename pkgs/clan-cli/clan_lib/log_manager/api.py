from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.log_manager import LogManager

LOG_MANAGER_INSTANCE: LogManager | None = None


@API.register
def list_log_days() -> list[str]:
    """List all available log days.

    Returns:
        A list of date strings in YYYY-MM-DD format representing all available log days.

    Raises:
        AssertionError: If LOG_MANAGER_INSTANCE is not initialized.
    """
    assert LOG_MANAGER_INSTANCE is not None
    return [day.date_day for day in LOG_MANAGER_INSTANCE.list_log_days()]


@API.register
def list_log_groups(
    selector: list[str] | None, date_day: str | None = None
) -> list[str]:
    """List all log groups at the specified hierarchical path.

    Args:
        selector: List of path components to navigate to. Empty list returns top-level groups.
        date_day: Optional date to filter by (YYYY-MM-DD format). If None, uses most recent day.

    Returns:
        A list of folder names (decoded) at the specified path level.

    Raises:
        AssertionError: If LOG_MANAGER_INSTANCE is not initialized.
    """
    assert LOG_MANAGER_INSTANCE is not None
    return LOG_MANAGER_INSTANCE.filter(selector, date_day=date_day)


@API.register
def get_log_file(
    id_key: str, selector: list[str] | None = None, date_day: str | None = None
) -> str:
    """Get the contents of a specific log file by operation key.

    Args:
        id_key: The operation key to search for.
        selector: Optional group path to search in. If None, searches all groups.
        date_day: Optional specific date to search in (YYYY-MM-DD format). If None, searches all days.

    Returns:
        The contents of the log file as a string.

    Raises:
        ClanError: If the log file is not found.
        AssertionError: If LOG_MANAGER_INSTANCE is not initialized.
    """
    assert LOG_MANAGER_INSTANCE is not None

    log_file = LOG_MANAGER_INSTANCE.get_log_file(
        op_key=id_key, selector=selector, date_day=date_day
    )
    if log_file is None:
        msg = f"Log file with op_key '{id_key}' not found in selector '{selector}' and date_day '{date_day}'."
        raise ClanError(msg)

    return log_file.get_file_path().read_text()
