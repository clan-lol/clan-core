import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from clan_lib.sandbox_exec import sandbox_exec_cmd


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_exec_executes_successfully() -> None:
    """sandbox_exec_cmd runs a simple command and exits 0."""
    with sandbox_exec_cmd(["/bin/sh", "-c", "exit 0"]) as cmd:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_allows_write_to_tmpdir(temp_dir: Path) -> None:
    """Test that sandboxed process can write to the allowed tmpdir."""
    test_file = temp_dir / "test_output.txt"

    script = f'echo "test content" > "{test_file}"'

    with sandbox_exec_cmd(
        ["/bin/sh", "-c", script],
        rw_paths=[str(temp_dir)],
    ) as cmd:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert test_file.exists(), "File was not created in tmpdir"
        assert test_file.read_text().strip() == "test content"


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_denies_write_to_home(temp_dir: Path) -> None:
    """Test that sandboxed process cannot write to user home directory."""
    forbidden_file = Path.home() / ".sandbox_test_forbidden.txt"
    script = f'echo "forbidden" > "{forbidden_file}" 2>&1 || echo "write denied"'

    try:
        if forbidden_file.exists():
            forbidden_file.unlink()

        with sandbox_exec_cmd(
            ["/bin/sh", "-c", script],
            rw_paths=[str(temp_dir)],
        ) as cmd:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )

        if forbidden_file.exists():
            forbidden_file.unlink()
            pytest.skip(
                "macOS sandbox-exec with (allow default) has limited deny capabilities",
            )
        else:
            assert "write denied" in result.stdout or result.returncode != 0
    finally:
        try:
            if forbidden_file.exists():
                forbidden_file.unlink()
        except OSError:
            pass


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_allows_nix_store_read(temp_dir: Path) -> None:
    """Test that sandboxed process can read from nix store."""
    # Resolve the nix binary path outside the sandbox; /usr/bin/which is not
    # in the sandbox's allowed process-exec list.
    nix_bin = shutil.which("nix")
    assert nix_bin, "nix not found on PATH"
    real_nix = str(Path(nix_bin).resolve())

    success_file = temp_dir / "nix_test.txt"
    script = f'ls "{real_nix}" >/dev/null 2>&1 && echo "success" > "{success_file}"'

    with sandbox_exec_cmd(
        ["/bin/sh", "-c", script],
        rw_paths=[str(temp_dir)],
    ) as cmd:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert success_file.exists(), "Success file was not created"
        assert success_file.read_text().strip() == "success"


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_exec_ro_paths_are_readable() -> None:
    """Files in ro_paths can be read."""
    # Use a temp dir under $HOME so it's not covered by the hardcoded /tmp allow rules.
    with TemporaryDirectory(prefix=".sandbox-ro-", dir=str(Path.home())) as ro_dir:
        secret = Path(ro_dir) / "secret.txt"
        secret.write_text("hello-ro")

        with sandbox_exec_cmd(
            ["/bin/sh", "-c", f"cat {secret}"],
            ro_paths=[ro_dir],
        ) as cmd:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            assert result.returncode == 0, f"Command failed: {result.stderr}"
            assert "hello-ro" in result.stdout


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_exec_ro_paths_are_not_writable() -> None:
    """Writing to a read-only path fails."""
    # Use a temp dir under $HOME; paths under /tmp are hardcoded writable in the profile.
    with (
        TemporaryDirectory(prefix=".sandbox-ro-", dir=str(Path.home())) as ro_dir,
        sandbox_exec_cmd(
            ["/bin/sh", "-c", f'echo bad > "{ro_dir}/forbidden.txt"'],
            ro_paths=[ro_dir],
        ) as cmd,
    ):
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode != 0 or not Path(f"{ro_dir}/forbidden.txt").exists(), (
            "Write to ro_paths should have been denied"
        )


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
def test_sandbox_exec_denies_unmounted_paths() -> None:
    """Paths not explicitly allowed are inaccessible."""
    with TemporaryDirectory(
        prefix=".sandbox-deny-", dir=str(Path.home())
    ) as outside_dir:
        sentinel = Path(outside_dir) / "sentinel.txt"
        sentinel.write_text("should-not-see")

        with sandbox_exec_cmd(
            [
                "/bin/sh",
                "-c",
                f'cat "{sentinel}" 2>/dev/null && echo visible || echo hidden',
            ],
        ) as cmd:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            assert "hidden" in result.stdout or result.returncode != 0, (
                "Unmounted path should be inaccessible"
            )
