import argparse
import logging
import sys

from clan_cli.profiler import profile

from clan_app.app import ClanAppOptions, app_run

log = logging.getLogger(__name__)


@profile
def main(argv: list[str] = sys.argv) -> int:
    parser = argparse.ArgumentParser(description="Clan App")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run dev mode (default: False)",
    )
    parser.add_argument(
        "--dev-host",
        type=str,
        default="localhost",
        help="The host for the VITE dev server (default: localhost)",
    )
    parser.add_argument(
        "--dev-port",
        type=int,
        default=3000,
        help="The host and port for the VITE dev server (default: 3000)",
    )
    parser.add_argument(
        "--http-api",
        action="store_true",
        help="Enable HTTP API mode (default: False)",
    )
    parser.add_argument(
        "--http-host",
        type=str,
        default="localhost",
        help="The host for the HTTP API server (default: localhost)",
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=3192,
        help="The host and port for the HTTP API server (default: 3192)",
    )
    args = parser.parse_args(argv[1:])

    app_opts = ClanAppOptions(
        dev=args.dev,
        dev_host=args.dev_host,
        dev_port=args.dev_port,
        http_api=args.http_api,
        http_host=args.http_host,
        http_port=args.http_port,
        debug=args.debug,
    )
    try:
        app_run(app_opts)
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received, exiting...")
        return 0

    return 0
