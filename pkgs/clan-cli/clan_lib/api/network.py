import logging
import time
from dataclasses import dataclass
from typing import Literal

from clan_cli.machines.machines import Machine

from clan_lib.api import API
from clan_lib.cmd import RunOpts
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


@dataclass
class ConnectionOptions:
    timeout: int = 2
    retries: int = 10


@API.register
def check_machine_online(
    machine: Machine, opts: ConnectionOptions | None = None
) -> Literal["Online", "Offline"]:
    hostname = machine.target_host_address
    if not hostname:
        msg = f"Machine {machine.name} does not specify a targetHost"
        raise ClanError(msg)

    timeout = opts.timeout if opts and opts.timeout else 2

    for _ in range(opts.retries if opts and opts.retries else 10):
        with machine.target_host() as target:
            res = target.run(
                ["true"],
                RunOpts(timeout=timeout, check=False, needs_user_terminal=True),
            )

            if res.returncode == 0:
                return "Online"
        time.sleep(timeout)

    return "Offline"
