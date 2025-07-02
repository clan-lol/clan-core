import logging

from clan_cli.profiler import profile

log = logging.getLogger(__name__)
import os
from dataclasses import dataclass
from pathlib import Path

import clan_lib.machines.actions  # noqa: F401
from clan_lib.api import API, tasks

# TODO: We have to manually import python files to make the API.register be triggered.
# We NEED to fix this, as this is super unintuitive and error-prone.
from clan_lib.api.tasks import list_tasks as dummy_list  # noqa: F401
from clan_lib.custom_logger import setup_logging
from clan_lib.dirs import user_data_dir
from clan_lib.log_manager import LogManager
from clan_lib.log_manager import api as log_manager_api

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

    # Init LogManager global in log_manager_api module
    log_manager_api.LOG_MANAGER_INSTANCE = LogManager(
        base_dir=user_data_dir() / "clan-app" / "logs"
    )

    # Init BAKEND_THREADS in tasks module
    tasks.BAKEND_THREADS = webview.threads

    API.overwrite_fn(open_file)
    webview.bind_jsonschema_api(API, log_manager=log_manager_api.LOG_MANAGER_INSTANCE)
    webview.size = Size(1280, 1024, SizeHint.NONE)
    webview.navigate(content_uri)
    webview.run()
    return 0
