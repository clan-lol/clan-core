from pathlib import Path

import pytest
from clan_lib.ssh.remote import Remote
from clan_lib.ssh.upload import upload


@pytest.mark.with_core
def test_upload_single_file(
    temporary_home: Path,
    hosts: list[Remote],
) -> None:
    host = hosts[0]

    src_file = temporary_home / "test.txt"
    src_file.write_text("test")
    dest_file = temporary_home / "test_dest.txt"
    with host.host_connection() as host:
        upload(host, src_file, dest_file)

    assert dest_file.exists()
    assert dest_file.read_text() == "test"
