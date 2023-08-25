import argparse
from typing import Callable, NoReturn, Optional

start_server: Optional[Callable] = None
ServerImportError: Optional[ImportError] = None
try:
    from .server import start_server
except ImportError as e:
    ServerImportError = e


def fastapi_is_not_installed(_: argparse.Namespace) -> NoReturn:
    assert ServerImportError is not None
    print(
        f"Dependencies for the webserver is not installed. The webui command has been disabled ({ServerImportError})"
    )
    exit(1)


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--port", type=int, default=2979, help="Port to listen on")
    parser.add_argument("--host", type=str, default="::1", help="Host to listen on")
    parser.add_argument(
        "--no-open", action="store_true", help="Don't open the browser", default=False
    )
    parser.add_argument(
        "--dev", action="store_true", help="Run in development mode", default=False
    )
    parser.add_argument(
        "--dev-port",
        type=int,
        default=3000,
        help="Port to listen on for the dev server",
    )
    parser.add_argument(
        "--dev-host", type=str, default="localhost", help="Host to listen on"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Don't reload on changes", default=False
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        help="Log level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
    )
    if start_server is None:
        parser.set_defaults(func=fastapi_is_not_installed)
    else:
        parser.set_defaults(func=start_server)
