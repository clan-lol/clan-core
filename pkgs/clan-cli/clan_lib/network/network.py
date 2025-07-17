import importlib
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from clan_cli.vars.get import get_machine_var
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.ssh.parse import parse_ssh_uri
from clan_lib.ssh.remote import Remote, check_machine_ssh_reachable

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Peer:
    _host: dict[str, str | dict[str, str]]
    flake: Flake

    @cached_property
    def host(self) -> str:
        if "plain" in self._host and isinstance(self._host["plain"], str):
            return self._host["plain"]
        if "var" in self._host and isinstance(self._host["var"], dict):
            _var: dict[str, str] = self._host["var"]
            var = get_machine_var(
                str(self.flake),
                _var["machine"],
                f"{_var['generator']}/{_var['file']}",
            )
            return var.value.decode()
        msg = f"Unknown Var Type {self._host}"
        raise ClanError(msg)


class NetworkTechnologyBase(ABC):
    @abstractmethod
    def is_running(self) -> bool:
        pass

    # TODO this will depend on the network implementation if we do user networking at some point, so it should be abstractmethod
    def ping(self, peer: Peer) -> None | float:
        if self.is_running():
            try:
                # Parse the peer's host address to create a Remote object, use peer here since we don't have the machine_name here
                remote = parse_ssh_uri(machine_name="peer", address=peer.host)

                # Use the existing SSH reachability check
                now = time.time()
                result = check_machine_ssh_reachable(remote)

                if result.ok:
                    return (time.time() - now) * 1000
                return None

            except Exception as e:
                log.debug(f"Error checking peer {peer.host}: {e}")
                return None
        return None


@dataclass(frozen=True)
class Network:
    peers: dict[str, Peer]
    module_name: str
    priority: int = 1000

    @cached_property
    def module(self) -> NetworkTechnologyBase:
        module = importlib.import_module(self.module_name)
        return module.NetworkTechnology()

    def is_running(self) -> bool:
        return self.module.is_running()

    def ping(self, peer: str) -> float | None:
        return self.module.ping(self.peers[peer])


def networks_from_flake(flake: Flake) -> dict[str, Network]:
    networks: dict[str, Network] = {}
    networks_ = flake.select("clan.exports.instances.*.networking")
    for network_name, network in networks_.items():
        if network:
            peers: dict[str, Peer] = {}
            for _peer in network["peers"].values():
                peers[_peer["name"]] = Peer(_host=_peer["host"], flake=flake)
            networks[network_name] = Network(
                peers=peers,
                module_name=network["module"],
                priority=network["priority"],
            )
    return networks


def get_best_remote(machine_name: str, networks: dict[str, Network]) -> Remote | None:
    for network_name, network in sorted(
        networks.items(), key=lambda network: -network[1].priority
    ):
        if machine_name in network.peers:
            if network.is_running() and network.ping(machine_name):
                print(f"connecting via {network_name}")
                return Remote.from_ssh_uri(
                    machine_name=machine_name,
                    address=network.peers[machine_name].host,
                )
    return None


def get_network_overview(networks: dict[str, Network]) -> dict:
    result: dict[str, dict[str, Any]] = {}
    for network_name, network in networks.items():
        result[network_name] = {}
        result[network_name]["status"] = None
        result[network_name]["peers"] = {}
        network_online = False
        if network.module.is_running():
            result[network_name]["status"] = True
            network_online = True
        for peer_name in network.peers:
            if network_online:
                try:
                    result[network_name]["peers"][peer_name] = network.ping(peer_name)
                except ClanError:
                    log.warning(
                        f"getting host for machine: {peer_name} in network: {network_name} failed"
                    )
            else:
                result[network_name]["peers"][peer_name] = None
    return result
