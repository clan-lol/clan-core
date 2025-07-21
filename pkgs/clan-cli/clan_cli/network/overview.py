import argparse
import logging

from clan_lib.flake import require_flake
from clan_lib.network.network import get_network_overview, networks_from_flake

log = logging.getLogger(__name__)


def overview_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    networks = networks_from_flake(flake)
    overview = get_network_overview(networks)
    for network_name, network in overview.items():
        print(f"{network_name} {'[ONLINE]' if network['status'] else '[OFFLINE]'}")
        for peer_name, peer in network["peers"].items():
            print(f"\t{peer_name}: {'[OFFLINE]' if not peer else f'[{peer}]'}")


def register_overview_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=overview_command)
