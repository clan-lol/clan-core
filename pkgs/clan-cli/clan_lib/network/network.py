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

if TYPE_CHECKING:
    from clan_lib.ssh.remote import Remote

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
            return var.value.decode()
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
        return self.module.ping(self.peers[peer])

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
    def ping(self, peer: Peer) -> None | float:
        pass

    @contextmanager
    @abstractmethod
    def connection(self, network: Network) -> Iterator[Network]:
        pass


def networks_from_flake(flake: Flake) -> dict[str, Network]:
    # TODO more precaching, for example for vars
    flake.precache(
        [
            "clan.exports.instances.*.networking",
        ]
    )
    networks: dict[str, Network] = {}
    networks_ = flake.select("clan.exports.instances.*.networking")
    for network_name, network in networks_.items():
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


def get_best_network(machine_name: str, networks: dict[str, Network]) -> Network | None:
    for network_name, network in sorted(
        networks.items(), key=lambda network: -network[1].priority
    ):
        if machine_name in network.peers:
            if network.is_running() and network.ping(machine_name):
                print(f"connecting via {network_name}")
                return network
    return None


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
