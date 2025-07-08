import logging
import os
from dataclasses import dataclass
from pathlib import Path

from clan_cli.profiler import profile
from clan_lib.api import API, load_in_all_api_functions, tasks
from clan_lib.custom_logger import setup_logging
from clan_lib.dirs import user_data_dir
from clan_lib.log_manager import LogGroupConfig, LogManager
from clan_lib.log_manager import api as log_manager_api

from clan_app.api.file_gtk import open_file
from clan_app.deps.webview.middleware import (
    ArgumentParsingMiddleware,
    LoggingMiddleware,
    MethodExecutionMiddleware,
)
from clan_app.deps.webview.webview import Size, SizeHint, Webview

log = logging.getLogger(__name__)


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

    # Add a log group ["clans", <dynamic_name>, "machines", <dynamic_name>]
    log_manager = LogManager(base_dir=user_data_dir() / "clan-app" / "logs")
    clan_log_group = LogGroupConfig("clans", "Clans").add_child(
        LogGroupConfig("machines", "Machines")
    )
    log_manager = log_manager.add_root_group_config(clan_log_group)
    # Init LogManager global in log_manager_api module
    log_manager_api.LOG_MANAGER_INSTANCE = log_manager

    # Populate the API global with all functions
    load_in_all_api_functions()
    API.overwrite_fn(open_file)

    webview = Webview(
        debug=app_opts.debug, title="Clan App", size=Size(1280, 1024, SizeHint.NONE)
    )

    # Add middleware to the webview
    webview.add_middleware(ArgumentParsingMiddleware(api=API))
    webview.add_middleware(LoggingMiddleware(log_manager=log_manager))
    webview.add_middleware(MethodExecutionMiddleware(api=API))

    # Init BAKEND_THREADS global in tasks module
    tasks.BAKEND_THREADS = webview.threads

    webview.bind_jsonschema_api(API, log_manager=log_manager)
    webview.navigate(content_uri)
    webview.run()
    return 0
