import argparse
import logging
import sys

from clan_cli.profiler import profile

from clan_app.app import ClanAppOptions, app_run

log = logging.getLogger(__name__)


@profile
def main(argv: list[str] = sys.argv) -> int:
    parser = argparse.ArgumentParser(description="Clan App")
    parser.add_argument(
        "--content-uri",
        type=str,
        help="The URI of the content to display",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
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
        default=8080,
        help="The host and port for the HTTP API server (default: 8080)",
    )
    args = parser.parse_args(argv[1:])

    app_opts = ClanAppOptions(
        content_uri=args.content_uri,
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
