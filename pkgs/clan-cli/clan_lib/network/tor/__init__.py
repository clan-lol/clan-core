import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from clan_lib.errors import ClanError
from clan_lib.network import Network, NetworkTechnologyBase, Peer
from clan_lib.network.tor.lib import is_tor_running, spawn_tor
from clan_lib.ssh.remote import Remote
from clan_lib.ssh.socks_wrapper import tor_wrapper

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class NetworkTechnology(NetworkTechnologyBase):
    @property
    def proxy(self) -> int:
        """Return the SOCKS5 proxy port for this network technology."""
        return 9050

    def is_running(self) -> bool:
        """Check if Tor is running by sending HTTP request to SOCKS port."""
        return is_tor_running(self.proxy)

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
        if self.is_running():
            yield network
        else:
            with spawn_tor() as _:
                yield network

    def remote(self, peer: Peer) -> list["Remote"]:
        return [
            Remote(
                address=host,
                user=peer.ssh_user,
                port=peer.port,
                command_prefix=peer.name,
                socks_port=self.proxy,
                socks_wrapper=tor_wrapper,
            )
            for host in peer.host
        ]
