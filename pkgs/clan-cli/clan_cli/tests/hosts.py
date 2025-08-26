import os
import pwd
from pathlib import Path

import pytest
from clan_cli.tests.sshd import Sshd
from clan_lib.ssh.remote import Remote


@pytest.fixture
def hosts(sshd: Sshd) -> list[Remote]:
    login = pwd.getpwuid(os.getuid()).pw_name
    return [
        Remote(
            address="127.0.0.1",
            port=sshd.port,
            user=login,
            private_key=Path(sshd.key),
            host_key_check="none",
            command_prefix="local_test",
        ),
    ]
