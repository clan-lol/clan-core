import argparse
import logging
import os
import subprocess
import time
import urllib.request
import webbrowser
from contextlib import ExitStack, contextmanager
from pathlib import Path
from threading import Thread
from typing import Iterator

# XXX: can we dynamically load this using nix develop?
from uvicorn import run

logger = logging.getLogger(__name__)


def defer_open_browser(base_url: str) -> None:
    for i in range(5):
        try:
            urllib.request.urlopen(base_url + "/health")
            break
        except OSError:
            time.sleep(i)
    webbrowser.open(base_url)


@contextmanager
def spawn_node_dev_server() -> Iterator[None]:
    logger.info("Starting node dev server...")
    path = Path(__file__).parent.parent.parent.parent / "ui"
    with subprocess.Popen(
        ["direnv", "exec", path, "npm", "run", "dev"],
        cwd=path,
    ) as proc:
        try:
            yield
        finally:
            proc.terminate()


def start_server(args: argparse.Namespace) -> None:
    with ExitStack() as stack:
        if args.dev:
            os.environ["CLAN_WEBUI_ENV"] = "development"
            os.environ["CLAN_WEBUI_DEV_PORT"] = str(args.dev_port)
            os.environ["CLAN_WEBUI_DEV_HOST"] = args.dev_host

            stack.enter_context(spawn_node_dev_server())

            open_url = f"http://{args.dev_host}:{args.dev_port}"
        else:
            os.environ["CLAN_WEBUI_ENV"] = "production"
            open_url = f"http://[{args.host}]:{args.port}"

        if not args.no_open:
            Thread(target=defer_open_browser, args=(open_url,)).start()

        run(
            "clan_cli.webui.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
        )
