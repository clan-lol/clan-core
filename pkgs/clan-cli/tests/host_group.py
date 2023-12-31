import os
import pwd

import pytest
from sshd import Sshd

from clan_cli.ssh import Host, HostGroup, HostKeyCheck


@pytest.fixture
def host_group(sshd: Sshd) -> HostGroup:
    login = pwd.getpwuid(os.getuid()).pw_name
    return HostGroup(
        [
            Host(
                "127.0.0.1",
                port=sshd.port,
                user=login,
                key=sshd.key,
                host_key_check=HostKeyCheck.NONE,
            )
        ]
    )
