import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from clan_lib.sandbox_exec import bubblewrap_cmd


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_allows_write_to_tmpdir(temp_dir: Path) -> None:
    """Test that sandboxed process can write to the allowed tmpdir."""
    test_file = temp_dir / "test_output.txt"

    script = f'echo "test content" > "{test_file}"'

    cmd = bubblewrap_cmd(
        ["/bin/sh", "-c", script],
        rw_binds=[(str(temp_dir), str(temp_dir))],
    )
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert test_file.exists(), "File was not created in tmpdir"
    assert test_file.read_text().strip() == "test content"


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_denies_write_to_home(temp_dir: Path) -> None:
    """Test that sandboxed process cannot write to user home directory."""
    forbidden_file = Path.home() / ".sandbox_test_forbidden.txt"
    script = f'echo "forbidden" > "{forbidden_file}" 2>&1 || echo "write denied"'

    try:
        if forbidden_file.exists():
            forbidden_file.unlink()

        cmd = bubblewrap_cmd(
            ["/bin/sh", "-c", script],
            rw_binds=[(str(temp_dir), str(temp_dir))],
        )
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )

        assert not forbidden_file.exists(), "File was created though not allowed"
        assert "write denied" in result.stdout or result.returncode != 0
    finally:
        try:
            if forbidden_file.exists():
                forbidden_file.unlink()
        except OSError:
            pass


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_allows_nix_store_read(temp_dir: Path) -> None:
    """Test that sandboxed process can read from nix store."""
    success_file = temp_dir / "nix_test.txt"
    script = f'ls $(realpath $(which nix)) >/dev/null 2>&1 && echo "success" > "{success_file}"'

    cmd = bubblewrap_cmd(
        ["/bin/sh", "-c", script],
        rw_binds=[(str(temp_dir), str(temp_dir))],
    )
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert success_file.exists(), "Success file was not created"
    assert success_file.read_text().strip() == "success"


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_executes_successfully() -> None:
    """bubblewrap_cmd runs a simple command and exits 0."""
    cmd = bubblewrap_cmd(["/bin/sh", "-c", "exit 0"])
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed: {result.stderr}"


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_ro_bind_is_readable() -> None:
    """Files in a read-only bind mount can be read."""
    with TemporaryDirectory(prefix="bwrap-ro-") as ro_dir:
        secret = Path(ro_dir) / "secret.txt"
        secret.write_text("hello-ro")

        cmd = bubblewrap_cmd(
            ["/bin/sh", "-c", f"cat {secret}"],
            ro_binds=[(ro_dir, ro_dir)],
        )
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "hello-ro" in result.stdout


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_ro_bind_is_not_writable() -> None:
    """Writing to a read-only bind mount fails."""
    with TemporaryDirectory(prefix="bwrap-ro-") as ro_dir:
        cmd = bubblewrap_cmd(
            ["/bin/sh", "-c", f'echo bad > "{ro_dir}/forbidden.txt"'],
            ro_binds=[(ro_dir, ro_dir)],
        )
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode != 0 or not Path(f"{ro_dir}/forbidden.txt").exists(), (
            "Write to ro_bind should have been denied"
        )


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_rw_bind_is_writable() -> None:
    """Files in a read-write bind mount can be written."""
    with TemporaryDirectory(prefix="bwrap-rw-") as rw_dir:
        output_file = Path(rw_dir) / "output.txt"

        cmd = bubblewrap_cmd(
            ["/bin/sh", "-c", f'echo "hello-rw" > "{output_file}"'],
            rw_binds=[(rw_dir, rw_dir)],
        )
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists(), "File was not created in rw_bind"
        assert output_file.read_text().strip() == "hello-rw"


@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_denies_unmounted_paths() -> None:
    """Paths not explicitly mounted are inaccessible."""
    with TemporaryDirectory(prefix="bwrap-outside-") as outside_dir:
        sentinel = Path(outside_dir) / "sentinel.txt"
        sentinel.write_text("should-not-see")

        cmd = bubblewrap_cmd(
            [
                "/bin/sh",
                "-c",
                f'cat "{sentinel}" 2>/dev/null && echo visible || echo hidden',
            ],
        )
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        assert "hidden" in result.stdout or result.returncode != 0, (
            "Unmounted path should be inaccessible"
        )
