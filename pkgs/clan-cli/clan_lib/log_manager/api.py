from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.log_manager import LogManager

LOG_MANAGER_INSTANCE: LogManager | None = None


@API.register
def list_log_days() -> list[str]:
    """List all logs."""
    assert LOG_MANAGER_INSTANCE is not None
    return [day.date_day for day in LOG_MANAGER_INSTANCE.list_log_days()]


@API.register
def list_log_groups(selector: list[str], date_day: str | None = None) -> list[str]:
    """List all log groups."""
    assert LOG_MANAGER_INSTANCE is not None
    return LOG_MANAGER_INSTANCE.filter(selector, date_day=date_day)


@API.register
def get_log_file(
    id_key: str, selector: list[str] | None = None, date_day: str | None = None
) -> str:
    """Get a specific log file by op_key, function name and day."""
    assert LOG_MANAGER_INSTANCE is not None

    log_file = LOG_MANAGER_INSTANCE.get_log_file(
        op_key=id_key, selector=selector, date_day=date_day
    )
    if log_file is None:
        msg = f"Log file with op_key '{id_key}' not found in selector '{selector}' and date_day '{date_day}'."
        raise ClanError(msg)

    return log_file.get_file_path().read_text()
