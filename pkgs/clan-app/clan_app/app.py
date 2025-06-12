import logging

from clan_cli.profiler import profile

log = logging.getLogger(__name__)
import os
from dataclasses import dataclass
from pathlib import Path

import clan_lib.machines.actions  # noqa: F401
from clan_lib.api import API, ApiError, ErrorDataClass, SuccessDataClass
from clan_lib.api.log_manager import LogDayDir, LogFile, LogFuncDir, LogManager

# TODO: We have to manually import python files to make the API.register be triggered.
# We NEED to fix this, as this is super unintuitive and error-prone.
from clan_lib.api.tasks import list_tasks as dummy_list  # noqa: F401
from clan_lib.custom_logger import setup_logging
from clan_lib.dirs import user_data_dir

from clan_app.api.file_gtk import open_file
from clan_app.deps.webview.webview import Size, SizeHint, Webview


@dataclass
class ClanAppOptions:
    content_uri: str
    debug: bool


@profile
def app_run(app_opts: ClanAppOptions) -> int:
    if app_opts.debug:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)

    log.debug("Debug mode enabled")

    if app_opts.content_uri:
        content_uri = app_opts.content_uri
    else:
        site_index: Path = Path(os.getenv("WEBUI_PATH", ".")).resolve() / "index.html"
        content_uri = f"file://{site_index}"

    webview = Webview(debug=app_opts.debug)
    webview.title = "Clan App"
    # This seems to call the gtk api correctly but and gtk also seems to our icon, but somehow the icon is not loaded.
    webview.icon = "clan-white"

    log_manager = LogManager(base_dir=user_data_dir() / "clan-app" / "logs")

    def cancel_task(
        task_id: str, *, op_key: str
    ) -> SuccessDataClass[None] | ErrorDataClass:
        """Cancel a task by its op_key."""
        log.debug(f"Cancelling task with op_key: {task_id}")
        future = webview.threads.get(task_id)
        if future:
            future.stop_event.set()
            log.debug(f"Task {task_id} cancelled.")
        else:
            log.warning(f"Task {task_id} not found.")
        return SuccessDataClass(
            op_key=op_key,
            data=None,
            status="success",
        )

    def list_tasks(
        *,
        op_key: str,
    ) -> SuccessDataClass[list[str]] | ErrorDataClass:
        """List all tasks."""
        log.debug("Listing all tasks.")
        tasks = list(webview.threads.keys())
        return SuccessDataClass(
            op_key=op_key,
            data=tasks,
            status="success",
        )

    def list_log_days(
        *, op_key: str
    ) -> SuccessDataClass[list[LogDayDir]] | ErrorDataClass:
        """List all log days."""
        log.debug("Listing all log days.")
        return SuccessDataClass(
            op_key=op_key,
            data=log_manager.list_log_days(),
            status="success",
        )

    def list_log_funcs_at_day(
        day: str, *, op_key: str
    ) -> SuccessDataClass[list[LogFuncDir]] | ErrorDataClass:
        """List all log functions at a specific day."""
        log.debug(f"Listing all log functions for day: {day}")
        try:
            log_day_dir = LogDayDir(date_day=day, _base_dir=log_manager.base_dir)
        except ValueError:
            return ErrorDataClass(
                op_key=op_key,
                status="error",
                errors=[
                    ApiError(
                        message="Invalid day format",
                        description=f"Day {day} is not in the correct format (YYYY-MM-DD).",
                        location=["app::list_log_funcs_at_day", "day"],
                    )
                ],
            )
        return SuccessDataClass(
            op_key=op_key,
            data=log_day_dir.get_log_files(),
            status="success",
        )

    def list_log_files(
        day: str, func_name: str, *, op_key: str
    ) -> SuccessDataClass[list[LogFile]] | ErrorDataClass:
        """List all log functions at a specific day."""
        log.debug(f"Listing all log functions for day: {day}")

        try:
            log_func_dir = LogFuncDir(
                date_day=day, func_name=func_name, _base_dir=log_manager.base_dir
            )
        except ValueError:
            return ErrorDataClass(
                op_key=op_key,
                status="error",
                errors=[
                    ApiError(
                        message="Invalid day format",
                        description=f"Day {day} is not in the correct format (YYYY-MM-DD).",
                        location=["app::list_log_files", "day"],
                    )
                ],
            )
        return SuccessDataClass(
            op_key=op_key,
            data=log_func_dir.get_log_files(),
            status="success",
        )

    def get_log_file(
        id_key: str, *, op_key: str
    ) -> SuccessDataClass[str] | ErrorDataClass:
        """Get a specific log file."""

        try:
            log_file = log_manager.get_log_file(id_key)
        except ValueError:
            return ErrorDataClass(
                op_key=op_key,
                status="error",
                errors=[
                    ApiError(
                        message="Invalid log file ID",
                        description=f"Log file ID {id_key} is not in the correct format.",
                        location=["app::get_log_file", "id_key"],
                    )
                ],
            )

        if not log_file:
            return ErrorDataClass(
                op_key=op_key,
                status="error",
                errors=[
                    ApiError(
                        message="Log file not found",
                        description=f"Log file with id {id_key} not found.",
                        location=["app::get_log_file", "id_key"],
                    )
                ],
            )

        log_file_path = log_file.get_file_path()
        return SuccessDataClass(
            op_key=op_key,
            data=log_file_path.read_text(encoding="utf-8"),
            status="success",
        )

    API.overwrite_fn(list_tasks)
    API.overwrite_fn(open_file)
    API.overwrite_fn(cancel_task)
    API.overwrite_fn(list_log_days)
    API.overwrite_fn(list_log_funcs_at_day)
    API.overwrite_fn(list_log_files)
    API.overwrite_fn(get_log_file)
    webview.bind_jsonschema_api(API, log_manager=log_manager)
    webview.size = Size(1280, 1024, SizeHint.NONE)
    webview.navigate(content_uri)
    webview.run()
    return 0
