from pathlib import Path

import pytest
from clan_cli.ssh.host import Host, HostKeyCheck
from clan_cli.ssh.upload import upload


@pytest.mark.with_core
def test_upload_single_file(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    hosts: list[Host],
) -> None:
    host = hosts[0]
    host.host_key_check = HostKeyCheck.NONE

    src_file = temporary_home / "test.txt"
    src_file.write_text("test")
    dest_file = temporary_home / "test_dest.txt"

    upload(host, src_file, dest_file)

    assert dest_file.exists()
    assert dest_file.read_text() == "test"
