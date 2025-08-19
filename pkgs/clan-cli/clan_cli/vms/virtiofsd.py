import contextlib
import logging
import shutil
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.nix import nix_shell, nix_test_store

log = logging.getLogger(__name__)


@contextlib.contextmanager
def start_virtiofsd(socket_path: Path) -> Iterator[None]:
    sandbox = "namespace"
    if shutil.which("newuidmap") is None:
        sandbox = "none"
    store_root = nix_test_store() or Path("/")
    store = store_root / "nix" / "store"

    virtiofsd = nix_shell(
        ["virtiofsd"],
        [
            "virtiofsd",
            "--socket-path",
            str(socket_path),
            "--cache",
            "always",
            "--sandbox",
            sandbox,
            "--shared-dir",
            str(store),
        ],
    )
    log.debug("$ {}".format(" ".join(virtiofsd)))
    with subprocess.Popen(virtiofsd) as proc:
        try:
            while not socket_path.exists():
                rc = proc.poll()
                if rc is not None:
                    msg = f"virtiofsd exited unexpectedly with code {rc}"
                    raise ClanError(msg)
                time.sleep(0.1)
            yield
        finally:
            proc.kill()
