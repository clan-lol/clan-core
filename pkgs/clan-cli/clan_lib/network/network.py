import logging
import textwrap
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any

from clan_cli.vars.get import get_machine_var

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.import_utils import ClassSource, import_with_source
from clan_lib.ssh.remote import Remote

if TYPE_CHECKING:
    from clan_lib.machines.machines import Machine

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Peer:
    name: str
    _host: dict[str, str | dict[str, str]]
    flake: Flake

    @cached_property
    def host(self) -> str:
        if "plain" in self._host and isinstance(self._host["plain"], str):
            return self._host["plain"]
        if "var" in self._host and isinstance(self._host["var"], dict):
            _var: dict[str, str] = self._host["var"]
            machine_name = _var["machine"]
            generator = _var["generator"]
            var = get_machine_var(
                str(
                    self.flake
                ),  # TODO we should really pass the flake instance here instead of a str representation
                machine_name,
                f"{generator}/{_var['file']}",
            )
            if not var.exists:
                msg = (
                    textwrap.dedent(f"""
                It looks like you added a networking module to your machine, but forgot
                to deploy your changes. Please run "clan machines update {machine_name}"
                so that the appropriate vars are generated and deployed properly.
                """)
                    .rstrip("\n")
                    .lstrip("\n")
                )
                raise ClanError(msg)
            return var.value.decode().strip()
        msg = f"Unknown Var Type {self._host}"
        raise ClanError(msg)


@dataclass(frozen=True)
class Network:
    peers: dict[str, Peer]
    module_name: str
    priority: int = 1000

    @cached_property
    def module(self) -> "NetworkTechnologyBase":
        res = import_with_source(
            self.module_name,
            "NetworkTechnology",
            NetworkTechnologyBase,  # type: ignore[type-abstract]
        )
        return res

    def is_running(self) -> bool:
        return self.module.is_running()

    def ping(self, peer: str) -> float | None:
        return self.module.ping(self.remote(peer))

    def remote(self, peer: str) -> "Remote":
        # TODO raise exception if peer is not in peers
        return self.module.remote(self.peers[peer])


@dataclass(frozen=True)
class NetworkTechnologyBase(ABC):
    source: ClassSource

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def remote(self, peer: Peer) -> "Remote":
        pass

    @abstractmethod
    def ping(self, remote: "Remote") -> None | float:
        pass

    @contextmanager
    @abstractmethod
    def connection(self, network: Network) -> Iterator[Network]:
        pass


def networks_from_flake(flake: Flake) -> dict[str, Network]:
    # TODO more precaching, for example for vars
    flake.precache(
        [
            "clan.?exports.instances.*.networking",
        ]
    )
    networks: dict[str, Network] = {}
    networks_ = flake.select("clan.?exports.instances.*.networking")
    if "exports" not in networks_:
        msg = """You are not exporting the clan exports through your flake.
        Please add exports next to clanInternals and nixosConfiguration into the global flake.
        """
        log.warning(msg)
        return {}
    for network_name, network in networks_["exports"].items():
        if network:
            peers: dict[str, Peer] = {}
            for _peer in network["peers"].values():
                peers[_peer["name"]] = Peer(
                    name=_peer["name"], _host=_peer["host"], flake=flake
                )
            networks[network_name] = Network(
                peers=peers,
                module_name=network["module"],
                priority=network["priority"],
            )
    return networks


@contextmanager
def get_best_remote(machine: "Machine") -> Iterator["Remote"]:
    """
    Context manager that yields the best remote connection for a machine following this priority:
    1. If machine has targetHost in inventory, return a direct connection
    2. Return the highest priority network where machine is reachable
    3. If no network works, try to get targetHost from machine nixos config

    Args:
        machine: Machine instance to connect to

    Yields:
        Remote object for connecting to the machine

    Raises:
        ClanError: If no connection method works
    """

    # Step 1: Check if targetHost is set in inventory
    inv_machine = machine.get_inv_machine()
    target_host = inv_machine.get("deploy", {}).get("targetHost")

    if target_host:
        log.debug(f"Using targetHost from inventory for {machine.name}: {target_host}")
        # Create a direct network with just this machine
        try:
            remote = Remote.from_ssh_uri(machine_name=machine.name, address=target_host)
            yield remote
            return
        except Exception as e:
            log.debug(f"Inventory targetHost not reachable for {machine.name}: {e}")

    # Step 2: Try existing networks by priority
    try:
        networks = networks_from_flake(machine.flake)

        sorted_networks = sorted(networks.items(), key=lambda x: -x[1].priority)

        for network_name, network in sorted_networks:
            if machine.name not in network.peers:
                continue

            # Check if network is running and machine is reachable
            log.debug(f"trying to connect via {network_name}")
            if network.is_running():
                try:
                    ping_time = network.ping(machine.name)
                    if ping_time is not None:
                        log.info(
                            f"Machine {machine.name} reachable via {network_name} network"
                        )
                        yield network.remote(machine.name)
                        return
                except Exception as e:
                    log.debug(f"Failed to reach {machine.name} via {network_name}: {e}")
            else:
                try:
                    log.debug(f"Establishing connection for network {network_name}")
                    with network.module.connection(network) as connected_network:
                        ping_time = connected_network.ping(machine.name)
                        if ping_time is not None:
                            log.info(
                                f"Machine {machine.name} reachable via {network_name} network after connection"
                            )
                            yield connected_network.remote(machine.name)
                            return
                except Exception as e:
                    log.debug(
                        f"Failed to establish connection to {machine.name} via {network_name}: {e}"
                    )
    except Exception as e:
        log.debug(f"Failed to use networking modules to determine machines remote: {e}")

    # Step 3: Try targetHost from machine nixos config
    try:
        target_host = machine.select('config.clan.core.networking."targetHost"')
        if target_host:
            log.debug(
                f"Using targetHost from machine config for {machine.name}: {target_host}"
            )
            # Check if reachable
            try:
                remote = Remote.from_ssh_uri(
                    machine_name=machine.name, address=target_host
                )
                yield remote
                return
            except Exception as e:
                log.debug(
                    f"Machine config targetHost not reachable for {machine.name}: {e}"
                )
    except Exception as e:
        log.debug(f"Could not get targetHost from machine config: {e}")

    # No connection method found
    msg = f"Could not find any way to connect to machine '{machine.name}'. No targetHost configured and machine not reachable via any network."
    raise ClanError(msg)


def get_network_overview(networks: dict[str, Network]) -> dict:
    result: dict[str, dict[str, Any]] = {}
    for network_name, network in networks.items():
        result[network_name] = {}
        result[network_name]["status"] = None
        result[network_name]["peers"] = {}
        module = network.module
        log.debug(f"Using network module: {module}")
        if module.is_running():
            result[network_name]["status"] = True
        else:
            with module.connection(network) as network:
                for peer_name in network.peers:
                    try:
                        result[network_name]["peers"][peer_name] = network.ping(
                            peer_name
                        )
                    except ClanError:
                        log.warning(
                            f"getting host for machine: {peer_name} in network: {network_name} failed"
                        )
    return result
