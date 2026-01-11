import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from clan_lib.errors import ClanError
from clan_lib.network.network import Network, NetworkTechnologyBase, Peer
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class NetworkTechnology(NetworkTechnologyBase):
    """Direct network connection technology - checks SSH connectivity"""

    def is_running(self) -> bool:
        """Direct connections are always 'running' as they don't require a daemon"""
        return True

    def ping(self, remote: Remote) -> None | float:
        if self.is_running():
            try:
                # Parse the peer's host address to create a Remote object, use peer here since we don't have the machine_name here
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
        # direct connections are always online and don't use SOCKS, so we just return the original network
        # TODO maybe we want to setup jumphosts for network access? but sounds complicated
        yield network

    def remote(self, peer: Peer) -> list[Remote]:
        return [
            Remote(
                address=host,
                user=peer.ssh_user,
                port=peer.port,
                command_prefix=peer.name,
            )
            for host in peer.host
        ]
