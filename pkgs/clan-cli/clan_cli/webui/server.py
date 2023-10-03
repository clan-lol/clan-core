import argparse
import logging
import multiprocessing as mp
import os
import socket
import subprocess
import sys
import syslog
import time
import urllib.request
import webbrowser
from contextlib import ExitStack, contextmanager
from pathlib import Path
from threading import Thread
from typing import Iterator

# XXX: can we dynamically load this using nix develop?
from uvicorn import run

log = logging.getLogger(__name__)


def defer_open_browser(base_url: str) -> None:
    for i in range(5):
        try:
            urllib.request.urlopen(base_url + "/health")
            break
        except OSError:
            time.sleep(i)
    webbrowser.open(base_url)


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
            Thread(target=defer_open_browser, args=(open_url,)).start()

        run(
            "clan_cli.webui.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
            access_log=args.log_level == "debug",
            headers=headers,
        )


# Define a function that takes the path of the file socket as input and returns True if it is served, False otherwise
def is_served(file_socket: Path) -> bool:
    # Create a Unix stream socket
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Try to connect to the file socket
    try:
        client.connect(str(file_socket))
        # Connection succeeded, return True
        return True
    except OSError:
        # Connection failed, return False
        return False
    finally:
        # Close the client socket
        client.close()


def set_out_to_syslog() -> None:  # type: ignore
    # Define some constants for convenience
    log_levels = {
        "emerg": syslog.LOG_EMERG,
        "alert": syslog.LOG_ALERT,
        "crit": syslog.LOG_CRIT,
        "err": syslog.LOG_ERR,
        "warning": syslog.LOG_WARNING,
        "notice": syslog.LOG_NOTICE,
        "info": syslog.LOG_INFO,
        "debug": syslog.LOG_DEBUG,
    }
    facility = syslog.LOG_USER  # Use user facility for custom applications

    # Open a connection to the system logger
    syslog.openlog("clan-cli", 0, facility)  # Use "myapp" as the prefix for messages

    # Define a custom write function that sends messages to syslog
    def write(message: str) -> int:
        # Strip the newline character from the message
        message = message.rstrip("\n")
        # Check if the message is not empty
        if message:
            # Send the message to syslog with the appropriate level
            if message.startswith("ERROR:"):
                # Use error level for messages that start with "ERROR:"
                syslog.syslog(log_levels["err"], message)
            else:
                # Use info level for other messages
                syslog.syslog(log_levels["info"], message)
        return 0

    # Assign the custom write function to sys.stdout and sys.stderr
    setattr(sys.stdout, "write", write)
    setattr(sys.stderr, "write", write)

    # Define a dummy flush function to prevent errors
    def flush() -> None:
        pass

    # Assign the dummy flush function to sys.stdout and sys.stderr
    setattr(sys.stdout, "flush", flush)
    setattr(sys.stderr, "flush", flush)


def _run_socketfile(socket_file: Path, debug: bool) -> None:
    set_out_to_syslog()
    run(
        "clan_cli.webui.app:app",
        uds=str(socket_file),
        access_log=debug,
        reload=False,
        log_level="debug" if debug else "info",
    )


@contextmanager
def api_server(debug: bool) -> Iterator[Path]:
    runtime_dir = os.getenv("XDG_RUNTIME_DIR")
    if runtime_dir is None:
        raise RuntimeError("XDG_RUNTIME_DIR not set")
    socket_path = Path(runtime_dir) / "clan.sock"
    socket_path = socket_path.resolve()

    log.debug("Socketfile lies at %s", socket_path)

    if not is_served(socket_path):
        log.debug("Starting api server...")
        mp.set_start_method(method="spawn")
        proc = mp.Process(target=_run_socketfile, args=(socket_path, debug))
        proc.start()
    else:
        log.info("Api server is already running on %s", socket_path)

    yield socket_path
    proc.terminate()
