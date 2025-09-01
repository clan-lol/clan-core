import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

from clan_cli.profiler import profile
from clan_lib.api import API, load_in_all_api_functions, tasks
from clan_lib.custom_logger import setup_logging
from clan_lib.dirs import user_data_dir
from clan_lib.log_manager import LogGroupConfig, LogManager
from clan_lib.log_manager import api as log_manager_api

from clan_app.api.file_gtk import get_clan_folder, get_system_file
from clan_app.api.middleware import (
    ArgumentParsingMiddleware,
    LoggingMiddleware,
    MethodExecutionMiddleware,
)
from clan_app.deps.http.http_server import HttpApiServer
from clan_app.deps.webview.webview import Size, SizeHint, Webview

log = logging.getLogger(__name__)


@dataclass
class ClanAppOptions:
    content_uri: str
    debug: bool
    http_api: bool = False
    http_host: str = "127.0.0.1"
    http_port: int = 8080


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
        LogGroupConfig("machines", "Machines"),
    )
    log_manager = log_manager.add_root_group_config(clan_log_group)
    # Init LogManager global in log_manager_api module
    log_manager_api.LOG_MANAGER_INSTANCE = log_manager

    # Populate the API global with all functions
    load_in_all_api_functions()

    # Create a shared threads dictionary for both HTTP and Webview modes
    shared_threads: dict[str, tasks.WebThread] = {}
    tasks.BAKEND_THREADS = shared_threads

    # Start HTTP API server if requested
    http_server = None
    if app_opts.http_api:
        openapi_file = os.getenv("OPENAPI_FILE", None)
        swagger_dist = os.getenv("SWAGGER_UI_DIST", None)

        http_server = HttpApiServer(
            api=API,
            openapi_file=Path(openapi_file) if openapi_file else None,
            swagger_dist=Path(swagger_dist) if swagger_dist else None,
            host=app_opts.http_host,
            port=app_opts.http_port,
            shared_threads=shared_threads,
        )

        # Add middleware to HTTP server
        http_server.add_middleware(ArgumentParsingMiddleware(api=API))
        http_server.add_middleware(LoggingMiddleware(log_manager=log_manager))
        http_server.add_middleware(MethodExecutionMiddleware(api=API))

        # Start the server (bridge will be created automatically)
        http_server.start()

        # HTTP-only mode - keep the server running
        log.info("HTTP API server running...")
        log.info(
            f"Swagger: http://{app_opts.http_host}:{app_opts.http_port}/api/swagger",
        )

        log.info("Press Ctrl+C to stop the server")
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Shutting down HTTP API server...")
            if http_server:
                http_server.stop()

    # Create webview if not running in HTTP-only mode
    if not app_opts.http_api:
        webview = Webview(
            debug=app_opts.debug,
            title="Clan App",
            size=Size(1280, 1024, SizeHint.NONE),
            shared_threads=shared_threads,
            app_id="org.clan.app",
        )

        API.overwrite_fn(get_system_file)
        API.overwrite_fn(get_clan_folder)

        # Add middleware to the webview
        webview.add_middleware(ArgumentParsingMiddleware(api=API))
        webview.add_middleware(LoggingMiddleware(log_manager=log_manager))
        webview.add_middleware(MethodExecutionMiddleware(api=API))

        webview.bind_jsonschema_api(API)
        webview.navigate(content_uri)
        webview.run()

    return 0
