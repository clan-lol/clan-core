from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.log_manager import LogDayDir, LogFile, LogFuncDir, LogGroupDir, LogManager

LOG_MANAGER_INSTANCE: LogManager | None = None


@API.register
def list_log_days() -> list[LogDayDir]:
    """List all logs."""
    assert LOG_MANAGER_INSTANCE is not None
    return LOG_MANAGER_INSTANCE.list_log_days()


@API.register
def list_log_groups(date_day: str) -> list[LogGroupDir]:
    """List all log groups."""
    assert LOG_MANAGER_INSTANCE is not None
    day_dir = LogDayDir(date_day, LOG_MANAGER_INSTANCE.base_dir)
    return day_dir.get_log_files()


@API.register
def list_log_funcs_at_day(date_day: str, group: str) -> list[LogFuncDir]:
    """List all logs for a specific function on a specific day."""
    assert LOG_MANAGER_INSTANCE is not None
    group_dir = LogGroupDir(date_day, group, LOG_MANAGER_INSTANCE.base_dir)
    return group_dir.get_log_files()


@API.register
def list_log_files(date_day: str, group: str, func_name: str) -> list[LogFile]:
    """List all log files for a specific function on a specific day."""
    assert LOG_MANAGER_INSTANCE is not None
    func_dir = LogFuncDir(date_day, group, func_name, LOG_MANAGER_INSTANCE.base_dir)
    return func_dir.get_log_files()


@API.register
def get_log_file(id_key: str, group: str | None = None) -> str:
    """Get a specific log file by op_key, function name and day."""
    assert LOG_MANAGER_INSTANCE is not None

    log_file = LOG_MANAGER_INSTANCE.get_log_file(id_key, specific_group=group)
    if log_file is None:
        return ""

    file_path = log_file.get_file_path()
    if not file_path.exists():
        msg = f"Log file {file_path} does not exist."
        raise ClanError(msg)

    return file_path.read_text()
