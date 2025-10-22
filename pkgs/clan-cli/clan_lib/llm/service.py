"""Service management for LLM (Ollama)."""

import logging
import time
import urllib.request
from http import HTTPStatus
from urllib.error import HTTPError, URLError

from clan_lib.api import API
from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.nix import nix_shell
from clan_lib.service_runner import create_service_manager

log = logging.getLogger(__name__)


@API.register
def run_llm_service() -> None:
    """Start the LLM service (Ollama)."""
    service_manager = create_service_manager()

    log.info("Downloading Ollama...")
    cmd = nix_shell(["ollama"], ["ollama"])
    run(cmd)  # Ensure ollama is downloaded

    # TODO: Detect GPU availability and choose appropriate Ollama package
    cmd = nix_shell(
        ["ollama"],
        ["ollama", "serve"],
    )
    service_manager.start_service("ollama", group="clan", command=cmd)

    start = time.time()
    timeout = 10.0  # seconds
    while True:
        try:
            with urllib.request.urlopen(
                "http://localhost:11434", timeout=5
            ) as response:
                status = response.getcode()
                body = response.read().decode(errors="ignore")
                if status == HTTPStatus.OK.value and "Ollama is running" in body:
                    break
        except (URLError, HTTPError, ConnectionRefusedError):
            log.info("Waiting for Ollama to start...")
        if time.time() - start >= timeout:
            logs = service_manager.get_service_logs("ollama")
            msg = f"Ollama did not start within 10 seconds: {logs}"
            raise ClanError(msg)
        time.sleep(0.5)


@API.register
def create_llm_model() -> None:
    """Ensure the Ollama model is available; pull it if missing."""
    model = "qwen3:4b-instruct"

    cmd = nix_shell(
        ["ollama"],
        ["ollama", "pull", model],
    )
    run(cmd)
    url = "http://localhost:11434/api/tags"

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
            if resp.getcode() == HTTPStatus.OK.value and model in resp.read().decode():
                return
    except HTTPError as e:
        msg = f"Ollama returned HTTP {e.code} when checking model availability."
        raise ClanError(msg) from e
    except URLError as e:
        msg = "Ollama API not reachable at http://localhost:11434"
        raise ClanError(msg) from e
