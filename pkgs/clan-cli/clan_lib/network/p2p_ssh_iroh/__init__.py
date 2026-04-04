import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cache

from clan_cli.vars.get import get_machine_var

from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import runtime_deps_flake
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
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

    def remote(self, peer: Peer, network: Network) -> list[Remote]:
        if network.instance_name is None:
            log.debug("p2p-ssh-iroh requires an instance name to resolve the ticket")
            return []

        dumbpipe = _dumbpipe_bin()
        generator_name = f"p2p-ssh-iroh-{network.instance_name}"

        machine = Machine(name=peer.name, flake=peer.flake)
        var = get_machine_var(machine, f"{generator_name}/ticket")

        if not var.exists:
            log.debug(
                f"p2p-ssh-iroh ticket var not found for {peer.name} "
                f"(generator={generator_name}). "
                f"Run 'clan machines update {peer.name}' to generate vars."
            )
            return []

        ticket = var.value.decode().strip()

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
        ]
