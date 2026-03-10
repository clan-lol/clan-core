import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from clan_lib.sandbox_exec import sandbox_bash, sandbox_cmd, sandbox_works

# --- sandbox_cmd tests ---


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_sandbox_cmd_executes_successfully() -> None:
    """sandbox_cmd runs a simple command and exits 0."""
    with sandbox_cmd(["/bin/sh", "-c", "exit 0"]) as cmd:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_sandbox_cmd_rw_paths_are_writable() -> None:
    """Files in rw_paths can be written through sandbox_cmd."""
    with TemporaryDirectory(prefix="sandbox-rw-") as rw_dir:
        output_file = Path(rw_dir) / "output.txt"
        with sandbox_cmd(
            ["/bin/sh", "-c", f'echo "hello" > "{output_file}"'],
            rw_paths=[rw_dir],
        ) as cmd:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            assert result.returncode == 0, f"Command failed: {result.stderr}"
            assert output_file.exists(), "File was not created via rw_paths"
            assert output_file.read_text().strip() == "hello"


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_sandbox_cmd_ro_paths_are_readable() -> None:
    """Files in ro_paths can be read through sandbox_cmd."""
    with TemporaryDirectory(prefix="sandbox-ro-") as ro_dir:
        secret = Path(ro_dir) / "secret.txt"
        secret.write_text("readable")
        with sandbox_cmd(
            ["/bin/sh", "-c", f"cat {secret}"],
            ro_paths=[ro_dir],
        ) as cmd:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            assert result.returncode == 0, f"Command failed: {result.stderr}"
            assert "readable" in result.stdout


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_sandbox_cmd_ro_paths_are_not_writable() -> None:
    """Files in ro_paths cannot be written through sandbox_cmd."""
    with (
        TemporaryDirectory(prefix="sandbox-ro-") as ro_dir,
        sandbox_cmd(
            ["/bin/sh", "-c", f'echo bad > "{ro_dir}/forbidden.txt"'],
            ro_paths=[ro_dir],
        ) as cmd,
    ):
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode != 0 or not Path(f"{ro_dir}/forbidden.txt").exists(), (
            "Write to ro_paths should have been denied"
        )


def test_sandbox_cmd_raises_on_unsupported_platform() -> None:
    """sandbox_cmd raises NotImplementedError on unsupported platforms."""
    with patch("clan_lib.sandbox_exec.sys") as mock_sys:
        mock_sys.platform = "freebsd"
        with (
            pytest.raises(NotImplementedError, match="not supported"),
            sandbox_cmd(["/bin/sh", "-c", "exit 0"]) as _cmd,
        ):
            pass


# --- sandbox_works tests ---


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_sandbox_works_returns_true_on_linux() -> None:
    """sandbox_works returns True on Linux with bubblewrap available."""
    sandbox_works.cache_clear()
    try:
        assert sandbox_works() is True
    finally:
        sandbox_works.cache_clear()


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_works_returns_true_on_darwin() -> None:
    """sandbox_works returns True on macOS with sandbox-exec available."""
    sandbox_works.cache_clear()
    try:
        assert sandbox_works() is True
    finally:
        sandbox_works.cache_clear()


def test_sandbox_works_returns_false_on_unsupported_platform() -> None:
    """sandbox_works returns False on unsupported platforms."""
    sandbox_works.cache_clear()
    try:
        with patch("clan_lib.sandbox_exec.sys") as mock_sys:
            mock_sys.platform = "freebsd"
            assert sandbox_works() is False
    finally:
        sandbox_works.cache_clear()


# --- sandbox_bash tests ---


def test_sandbox_bash_returns_bash_outside_nix_sandbox(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """sandbox_bash returns 'bash' when not in a nix sandbox."""
    sandbox_bash.cache_clear()
    try:
        monkeypatch.delenv("IN_NIX_SANDBOX", raising=False)
        assert sandbox_bash() == "bash"
    finally:
        sandbox_bash.cache_clear()


def test_sandbox_bash_resolves_path_in_nix_sandbox(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """sandbox_bash returns a resolved absolute path when IN_NIX_SANDBOX is set."""
    sandbox_bash.cache_clear()
    try:
        monkeypatch.setenv("IN_NIX_SANDBOX", "1")
        result = sandbox_bash()
        assert Path(result).is_absolute(), f"Expected absolute path, got {result}"
        assert Path(result).exists(), f"Resolved bash path does not exist: {result}"
    finally:
        sandbox_bash.cache_clear()
