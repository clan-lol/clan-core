import argparse
import logging
import os
import shutil
import subprocess
import time
import urllib.request
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from threading import Thread

# XXX: can we dynamically load this using nix develop?
import uvicorn
from pydantic import AnyUrl, IPvAnyAddress
from pydantic.tools import parse_obj_as

from clan_cli.errors import ClanError

log = logging.getLogger(__name__)


def open_browser(base_url: AnyUrl, sub_url: str) -> None:
    for i in range(5):
        try:
            urllib.request.urlopen(base_url + "/health")
            break
        except OSError:
            time.sleep(i)
    url = parse_obj_as(AnyUrl, f"{base_url}/{sub_url.removeprefix('/')}")
    _open_browser(url)


def _open_browser(url: AnyUrl) -> subprocess.Popen:
    for browser in ("firefox", "iceweasel", "iceape", "seamonkey"):
        if shutil.which(browser):
            # Do not add a new profile, as it will break in combination with
            # the -kiosk flag.
            cmd = [
                browser,
                "-kiosk",
                "-new-window",
                url,
            ]
            print(" ".join(cmd))
            return subprocess.Popen(cmd)
    for browser in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(browser):
            return subprocess.Popen([browser, f"--app={url}"])
    raise ClanError("No browser found")


@contextmanager
def spawn_node_dev_server(host: IPvAnyAddress, port: int) -> Iterator[None]:
    log.info("Starting node dev server...")
    path = Path(__file__).parent.parent.parent.parent / "ui"
    with subprocess.Popen(
        [
            "direnv",
            "exec",
            path,
            "npm",
            "run",
            "dev",
            "--",
            "--hostname",
            str(host),
            "--port",
            str(port),
        ],
        cwd=path,
    ) as proc:
        try:
            yield
        finally:
            proc.terminate()


def start_server(args: argparse.Namespace) -> None:
    os.environ["CLAN_WEBUI_ENV"] = "development" if args.dev else "production"

    with ExitStack() as stack:
        headers: list[tuple[str, str]] = []
        if args.dev:
            stack.enter_context(spawn_node_dev_server(args.dev_host, args.dev_port))

            base_url = f"http://{args.dev_host}:{args.dev_port}"
            host = args.dev_host
            if ":" in host:
                host = f"[{host}]"
        else:
            base_url = f"http://{args.host}:{args.port}"

        if not args.no_open:
            Thread(target=open_browser, args=(base_url, args.sub_url)).start()

        uvicorn.run(
            "clan_cli.webui.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
            access_log=args.log_level == "debug",
            headers=headers,
        )
