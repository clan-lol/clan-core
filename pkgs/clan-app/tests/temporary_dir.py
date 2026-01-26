import logging
import os
from pathlib import Path

import pytest

log = logging.getLogger(__name__)


# implementation copied from pkgs/clan-cli/clan_cli/tests/temporary_dir.py
@pytest.fixture
def temporary_home(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR")

    # Despite the new temporary home, we want nix to keep using the global nix cache
    cache_home = os.getenv("NIX_CACHE_HOME", os.environ["HOME"] + "/.cache")
    monkeypatch.setenv("NIX_CACHE_HOME", cache_home + "/nix")

    # Patch the home
    monkeypatch.setenv("HOME", str(temp_dir))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(temp_dir / ".config"))

    runtime_dir = temp_dir / "xdg-runtime-dir"
    runtime_dir.mkdir()
    runtime_dir.chmod(0o700)

    gpgdir = runtime_dir / "gpgagent"
    gpgdir.mkdir()
    gpgdir.chmod(0o700)
    monkeypatch.setenv("GPG_AGENT_INFO", str(gpgdir))

    # Iterate over all environment variables
    for key, value in os.environ.items():
        if xdg_runtime_dir and value.startswith(xdg_runtime_dir):
            monkeypatch.setenv(key, value.replace(xdg_runtime_dir, str(runtime_dir)))

    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.chdir(str(temp_dir))
    return temp_dir
