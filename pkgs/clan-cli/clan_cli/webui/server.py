import argparse
import time
import urllib.request
import webbrowser
from threading import Thread

from fastapi import FastAPI

# XXX: can we dynamically load this using nix develop?
from uvicorn import run

app = FastAPI()


@app.get("/health")
async def read_root() -> str:
    return "OK"


def defer_open_browser(base_url: str) -> None:
    for i in range(5):
        try:
            urllib.request.urlopen(base_url + "/health")
            break
        except OSError:
            time.sleep(i)
    webbrowser.open(base_url)


def start_server(args: argparse.Namespace) -> None:
    if not args.no_open:
        Thread(
            target=defer_open_browser, args=(f"http://[{args.host}]:{args.port}",)
        ).start()
    run(
        "clan_cli.webui.server:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
    )
