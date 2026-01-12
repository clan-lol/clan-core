import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from clan_lib.errors import ClanError
from clan_lib.network import Network, NetworkTechnologyBase, Peer
from clan_lib.network.zerotier.lib import check_zerotier_running
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class NetworkTechnology(NetworkTechnologyBase):
    def is_running(self) -> bool:
        return check_zerotier_running()

    def ping(self, remote: Remote) -> None | float:
        if self.is_running():
            try:
                # Use the existing SSH reachability check
                now = time.time()
                remote.check_machine_ssh_reachable()

                return (time.time() - now) * 1000

            except ClanError as e:
                log.debug(f"Error checking peer {remote}: {e}")
                return None
        return None

    @contextmanager
    def connection(self, network: Network) -> Iterator[Network]:
        # TODO: Implement userspace ZeroTier service start/stop
        yield network

    def remote(self, peer: Peer) -> list["Remote"]:
        return [
            Remote(
                address=host,
                user=peer.ssh_user,
                port=peer.port,
                command_prefix=peer.name,
            )
            for host in peer.host
        ]
