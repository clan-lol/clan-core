import logging
import time
from dataclasses import dataclass
from typing import Literal

from clan_lib.api import API
from clan_lib.cmd import RunOpts
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine

log = logging.getLogger(__name__)


@dataclass
class ConnectionOptions:
    timeout: int = 2
    retries: int = 10


@API.register
def check_machine_online(
    machine: Machine, opts: ConnectionOptions | None = None
) -> Literal["Online", "Offline"]:
    hostname = machine.target_host().target

    if not hostname:
        msg = f"Machine {machine.name} does not specify a targetHost"
        raise ClanError(msg)

    timeout = opts.timeout if opts and opts.timeout else 2

    for _ in range(opts.retries if opts and opts.retries else 10):
        host = machine.target_host()
        with host.ssh_control_master() as ssh:
            res = ssh.run(
                ["true"],
                RunOpts(timeout=timeout, check=False, needs_user_terminal=True),
            )

            if res.returncode == 0:
                return "Online"
        time.sleep(timeout)

    return "Offline"
