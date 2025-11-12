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
            from clan_lib.machines.machines import Machine  # noqa: PLC0415

            machine = Machine(name=machine_name, flake=self.flake)
            var = get_machine_var(
                machine,
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
        return import_with_source(
            self.module_name,
            "NetworkTechnology",
            NetworkTechnologyBase,  # type: ignore[type-abstract]
        )

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

@dataclass
class ExportScope():
    service: str
    instance: str
    role: str
    machine: str

def parse_export(exports: str) -> ExportScope:
    [service, instance, role, machine] = exports.split(":")
    return ExportScope(service, instance, role, machine)

def networks_from_flake(flake: Flake) -> dict[str, Network]:
    # TODO more precaching, for example for vars

    flake.precache([ "clan.?exports" ])

    networks: dict[str, Network] = {}

    defined_exports = flake.select("clan.?exports")

    if "exports" not in defined_exports:
        msg = """ NO EXPORTS! """
        log.warning(msg)
        return {}


    for export_name, network in defined_exports["exports"].items():

        if defined_exports["exports"][export_name]["networking"] is None:
            continue

        scope = parse_export(export_name)
        network_name = scope.instance
        peers: dict[str, Peer] = {}

        if "exports" not in defined_exports:
            msg = """
                Export has no export
            """
            log.warning(msg)
            continue

        for export_peer_name in defined_exports["exports"]:

            if defined_exports["exports"][export_peer_name]["peer"] is None:
                continue


            peer_scope = parse_export(export_peer_name)

            # Filter peers to only include those that belong to this network
            if peer_scope.service != scope.service or peer_scope.instance != network_name:
                continue

            peers[peer_scope.machine] = Peer(
                name=peer_scope.machine,
                _host=defined_exports["exports"][export_peer_name]["peer"]["host"],
                flake=flake,
            )

        networks[network_name] = Network(
            peers=peers,
            module_name=network["networking"]["module"],
            priority=network["priority"],
        )
    return networks


class BestRemoteContext:
    """Class-based context manager for establishing and maintaining network connections."""

    def __init__(self, machine: "Machine") -> None:
        self.machine = machine
        self._network_ctx: Any = None
        self._remote: Remote | None = None

    def __enter__(self) -> "Remote":
        """Establish the best remote connection for a machine following this priority:
        1. If machine has targetHost in inventory, return a direct connection
        2. Return the highest priority network where machine is reachable
        3. If no network works, try to get targetHost from machine nixos config

        Returns:
            Remote object for connecting to the machine

        Raises:
            ClanError: If no connection method works

        """
        # Step 1: Check if targetHost is set in inventory
        inv_machine = self.machine.get_inv_machine()
        target_host = inv_machine.get("deploy", {}).get("targetHost")

        if target_host:
            log.debug(
                f"Using targetHost from inventory for {self.machine.name}: {target_host}"
            )
            self._remote = Remote.from_ssh_uri(
                machine_name=self.machine.name, address=target_host
            )
            return self._remote

        # Step 2: Try existing networks by priority
        try:
            networks = networks_from_flake(self.machine.flake)
            sorted_networks = sorted(networks.items(), key=lambda x: -x[1].priority)

            for network_name, network in sorted_networks:
                if self.machine.name not in network.peers:
                    continue

                log.debug(f"trying to connect via {network_name}")
                if network.is_running():
                    try:
                        ping_time = network.ping(self.machine.name)
                        if ping_time is not None:
                            log.info(
                                f"Machine {self.machine.name} reachable via {network_name} network",
                            )
                            self._remote = remote = network.remote(self.machine.name)
                            return remote
                    except ClanError as e:
                        log.debug(
                            f"Failed to reach {self.machine.name} via {network_name}: {e}"
                        )
                else:
                    try:
                        log.debug(f"Establishing connection for network {network_name}")
                        # Enter the network context and keep it alive
                        self._network_ctx = network.module.connection(network)
                        connected_network = self._network_ctx.__enter__()
                        ping_time = connected_network.ping(self.machine.name)
                        if ping_time is not None:
                            log.info(
                                f"Machine {self.machine.name} reachable via {network_name} network after connection",
                            )
                            self._remote = remote = connected_network.remote(
                                self.machine.name
                            )
                            return remote
                        # Ping failed, clean up this connection attempt
                        self._network_ctx.__exit__(None, None, None)
                        self._network_ctx = None
                    except ClanError as e:
                        # Clean up failed connection attempt
                        if self._network_ctx is not None:
                            self._network_ctx.__exit__(None, None, None)
                            self._network_ctx = None
                        log.debug(
                            f"Failed to establish connection to {self.machine.name} via {network_name}: {e}",
                        )
        except (ImportError, AttributeError, KeyError) as e:
            log.debug(
                f"Failed to use networking modules to determine machines remote: {e}"
            )

        # Step 3: Try targetHost from machine nixos config
        target_host = self.machine.select('config.clan.core.networking."targetHost"')
        if target_host:
            log.debug(
                f"Using targetHost from machine config for {self.machine.name}: {target_host}",
            )
            self._remote = Remote.from_ssh_uri(
                machine_name=self.machine.name,
                address=target_host,
            )
            return self._remote

        # No connection method found
        msg = f"Could not find any way to connect to machine '{self.machine.name}'. No targetHost configured and machine not reachable via any network."
        raise ClanError(msg)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Clean up network connection if one was established."""
        if self._network_ctx is not None:
            self._network_ctx.__exit__(exc_type, exc_val, exc_tb)


def get_best_remote(machine: "Machine") -> BestRemoteContext:
    return BestRemoteContext(machine)


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
            with module.connection(network) as conn:
                for peer_name in conn.peers:
                    result[network_name]["peers"][peer_name] = conn.ping(
                        peer_name,
                    )
    return result
