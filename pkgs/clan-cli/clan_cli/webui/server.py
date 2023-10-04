import argparse
import logging
import os
import shutil
import signal
import subprocess
import tempfile
import time
import urllib.request
from contextlib import ExitStack, contextmanager
from pathlib import Path
from threading import Thread
from typing import Iterator

# XXX: can we dynamically load this using nix develop?
import uvicorn

from clan_cli.errors import ClanError

log = logging.getLogger(__name__)


def open_browser(base_url: str) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(5):
            try:
                urllib.request.urlopen(base_url + "/health")
                break
            except OSError:
                time.sleep(i)
        proc = _open_browser(base_url, tmpdir)
        try:
            proc.wait()
            print("Browser closed")
            os.kill(os.getpid(), signal.SIGINT)
        finally:
            proc.kill()
            proc.wait()


def _open_browser(base_url: str, tmpdir: str) -> subprocess.Popen:
    for browser in ("firefox", "iceweasel", "iceape", "seamonkey"):
        if shutil.which(browser):
            cmd = [
                browser,
                "-kiosk",
                "-private-window",
                "--new-instance",
                "--profile",
                tmpdir,
                base_url,
            ]
            print(" ".join(cmd))
            return subprocess.Popen(cmd)
    for browser in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(browser):
            return subprocess.Popen([browser, f"--app={base_url}"])
    raise ClanError("No browser found")


@contextmanager
def spawn_node_dev_server(host: str, port: int) -> Iterator[None]:
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
            host,
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
    with ExitStack() as stack:
        headers: list[tuple[str, str]] = []
        if args.dev:
            stack.enter_context(spawn_node_dev_server(args.dev_host, args.dev_port))

            open_url = f"http://{args.dev_host}:{args.dev_port}"
            host = args.dev_host
            if ":" in host:
                host = f"[{host}]"
            headers = [
                # (
                #     "Access-Control-Allow-Origin",
                #     f"http://{host}:{args.dev_port}",
                # ),
                # (
                #     "Access-Control-Allow-Methods",
                #     "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
                # ),
                # (
                #     "Allow",
                #     "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
                # )
            ]
        else:
            open_url = f"http://[{args.host}]:{args.port}"

        if not args.no_open:
            Thread(target=open_browser, args=(open_url,)).start()

        uvicorn.run(
            "clan_cli.webui.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
            access_log=args.log_level == "debug",
            headers=headers,
        )
