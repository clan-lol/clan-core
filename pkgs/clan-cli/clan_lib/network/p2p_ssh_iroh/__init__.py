import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cache

from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import runtime_deps_flake
from clan_lib.errors import ClanError
from clan_lib.network import Network, NetworkTechnologyBase, Peer
from clan_lib.nix.shell import _resolve_package
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


@cache
def _dumbpipe_bin() -> str:
    """Resolve the dumbpipe binary to a nix store path."""
    resolved = _resolve_package(runtime_deps_flake().resolve(), "dumbpipe")
    if resolved:
        return str(resolved.store_path / "bin" / resolved.exe_name)
    msg = "Failed to resolve dumbpipe package via nix"
    raise ClanError(msg)


@dataclass(frozen=True)
class NetworkTechnology(NetworkTechnologyBase):
    """p2p-ssh-iroh network — SSH over dumbpipe (iroh QUIC)."""

    def is_running(self) -> bool:
        return True

    def ping(self, remote: Remote) -> float | None:
        try:
            now = time.time()
            cmd = [
                *remote.ssh_cmd(control_master=False),
                "-o",
                "ConnectTimeout=15",
                "--",
                "true",
            ]
            run(cmd, RunOpts(timeout=20, needs_user_terminal=True))
            return (time.time() - now) * 1000
        except ClanError as e:
            log.debug(f"p2p-ssh-iroh ping failed for {remote}: {e}")
            return None

    @contextmanager
    def connection(self, network: Network) -> Iterator[Network]:
        yield network

    def remote(self, peer: Peer) -> list[Remote]:
        dumbpipe = _dumbpipe_bin()
        return [
            Remote(
                address=peer.name,
                user=peer.ssh_user,
                command_prefix=peer.name,
                host_key_check="accept-new",
                ssh_options={
                    "ProxyCommand": f"{dumbpipe} connect {ticket}",
                },
            )
            for ticket in peer.host
        ]
