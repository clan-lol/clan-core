import argparse
import logging

from clan_lib.flake import require_flake
from clan_lib.network.network import networks_from_flake

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    networks = networks_from_flake(flake)

    if not networks:
        print("No networks found")
        return

    # Calculate column widths
    col_network = max(12, max(len(name) for name in networks))
    col_priority = 8
    col_module = max(
        10, max(len(net.module_name.split(".")[-1]) for net in networks.values())
    )
    col_running = 8

    # Print header
    header = f"{'Network':<{col_network}}  {'Priority':<{col_priority}}  {'Module':<{col_module}}  {'Running':<{col_running}}  {'Peers'}"
    print(header)
    print("-" * len(header))

    # Print network entries
    for network_name, network in sorted(
        networks.items(), key=lambda network: -network[1].priority
    ):
        # Extract simple module name from full module path
        module_name = network.module_name.split(".")[-1]

        # Create peer list with truncation
        peer_names = list(network.peers.keys())
        max_peers_shown = 3

        if not peer_names:
            peers_str = "No peers"
        elif len(peer_names) <= max_peers_shown:
            peers_str = ", ".join(peer_names)
        else:
            shown_peers = peer_names[:max_peers_shown]
            remaining = len(peer_names) - max_peers_shown
            peers_str = f"{', '.join(shown_peers)} ...({remaining} more)"

        # Check if network is running
        try:
            is_running = network.is_running()
            running_status = "Yes" if is_running else "No"
        except Exception:
            running_status = "Error"

        print(
            f"{network_name:<{col_network}}  {network.priority:<{col_priority}}  {module_name:<{col_module}}  {running_status:<{col_running}}  {peers_str}"
        )


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
