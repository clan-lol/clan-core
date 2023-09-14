import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from host_group import HostGroup


def test_update(
    machine_flake: Path, host_group: HostGroup, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert len(host_group.hosts) == 1
    host = host_group.hosts[0]

    with TemporaryDirectory() as tmpdir:
        host.meta["flake_uri"] = machine_flake
        host.meta["flake_path"] = str(Path(tmpdir) / "rsync-target")
        host.ssh_options["SendEnv"] = "REALPATH"
        bin = Path(tmpdir).joinpath("bin")
        bin.mkdir()
        nixos_rebuild = bin.joinpath("nixos-rebuild")
        bash = shutil.which("bash")
        assert bash is not None
        nixos_rebuild.write_text(
            f"""#!{bash}
exit 0
"""
        )
        nixos_rebuild.chmod(0o755)
        f"{tmpdir}/bin:{os.environ['PATH']}"
        nix_state_dir = Path(tmpdir).joinpath("nix")
        nix_state_dir.mkdir()

        monkeypatch.setenv("REALPATH", str(nix_state_dir))
