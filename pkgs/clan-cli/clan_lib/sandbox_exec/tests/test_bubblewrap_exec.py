import subprocess
import sys
from pathlib import Path

import pytest
from clan_lib.sandbox_exec import bubblewrap_cmd


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_allows_write_to_tmpdir(temp_dir: Path) -> None:
    """Test that sandboxed process can write to the allowed tmpdir."""
    test_file = temp_dir / "test_output.txt"

    # Create a script that writes to the tmpdir using absolute path
    script = f'echo "test content" > "{test_file}"'

    cmd = bubblewrap_cmd(script, temp_dir)
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert test_file.exists(), "File was not created in tmpdir"
    assert test_file.read_text().strip() == "test content"


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_denies_write_to_home(temp_dir: Path) -> None:
    """Test that sandboxed process cannot write to user home directory."""
    # Try to write to a file in home directory (should be denied)
    forbidden_file = Path.home() / ".sandbox_test_forbidden.txt"
    script = f'echo "forbidden" > "{forbidden_file}" 2>&1 || echo "write denied"'

    try:
        # Ensure the file doesn't exist before test
        if forbidden_file.exists():
            forbidden_file.unlink()

        cmd = bubblewrap_cmd(script, temp_dir)
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )

        assert not forbidden_file.exists(), "File was created though not allowed"
        assert "write denied" in result.stdout or result.returncode != 0
    finally:
        # Clean up test file if it was created
        try:
            if forbidden_file.exists():
                forbidden_file.unlink()
        except OSError:
            pass


@pytest.mark.impure
@pytest.mark.skipif(sys.platform != "linux", reason="linux only")
def test_bubblewrap_allows_nix_store_read(temp_dir: Path) -> None:
    """Test that sandboxed process can read from nix store."""
    # Use ls to read from nix store (should work) and write result to file
    success_file = temp_dir / "nix_test.txt"
    script = f'ls $(realpath $(which nix)) >/dev/null 2>&1 && echo "success" > "{success_file}"'

    cmd = bubblewrap_cmd(script, temp_dir)
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert success_file.exists(), "Success file was not created"
    assert success_file.read_text().strip() == "success"
