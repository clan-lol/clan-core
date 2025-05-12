import logging

from clan_cli.profiler import profile

log = logging.getLogger(__name__)
import os
from dataclasses import dataclass
from pathlib import Path

from clan_cli.custom_logger import setup_logging
from clan_lib.api import API, ErrorDataClass, SuccessDataClass

from clan_app.api.file_gtk import open_file
from clan_app.deps.webview.webview import Size, SizeHint, Webview


@dataclass
class ClanAppOptions:
    content_uri: str
    debug: bool


@profile
def app_run(app_opts: ClanAppOptions) -> int:
    if app_opts.debug:
        setup_logging(logging.DEBUG, root_log_name=__name__.split(".")[0])
        setup_logging(logging.DEBUG, root_log_name="clan_cli")
    else:
        setup_logging(logging.INFO, root_log_name=__name__.split(".")[0])
        setup_logging(logging.INFO, root_log_name="clan_cli")

    log.debug("Debug mode enabled")

    if app_opts.content_uri:
        content_uri = app_opts.content_uri
    else:
        site_index: Path = Path(os.getenv("WEBUI_PATH", ".")).resolve() / "index.html"
        content_uri = f"file://{site_index}"

    webview = Webview(debug=app_opts.debug)

    def cancel_task(
        task_id: str, *, op_key: str
    ) -> SuccessDataClass[None] | ErrorDataClass:
        """Cancel a task by its op_key."""
        log.info(f"Cancelling task with op_key: {task_id}")
        with webview.lock:
            if task_id in webview.threads:
                future = webview.threads[task_id]
                future.stop_event.set()
                log.info(f"Task {task_id} cancelled.")
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
        log.info("Listing all tasks.")
        with webview.lock:
            tasks = list(webview.threads.keys())
        return SuccessDataClass(
            op_key=op_key,
            data=tasks,
            status="success",
        )

    API.overwrite_fn(list_tasks)
    API.overwrite_fn(open_file)
    API.overwrite_fn(cancel_task)
    webview.bind_jsonschema_api(API)
    webview.size = Size(1280, 1024, SizeHint.NONE)
    webview.navigate(content_uri)
    webview.run()
    return 0
