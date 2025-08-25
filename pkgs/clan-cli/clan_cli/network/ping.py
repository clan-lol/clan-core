import argparse
import logging

from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.network.network import networks_from_flake

log = logging.getLogger(__name__)


def ping_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = args.machine
    network_name = args.network

    networks = networks_from_flake(flake)

    if not networks:
        print("No networks found")
        return
    # If network is specified, only check that network
    if network_name:
        networks_to_check = [(network_name, networks[network_name])]

    else:
        # Sort networks by priority (highest first)
        networks_to_check = sorted(networks.items(), key=lambda x: -x[1].priority)

    found = False
    for net_name, network in networks_to_check:
        if machine in network.peers:
            found = True

            with network.module.connection(network) as conn:
                log.info(f"Pinging '{machine}' in network '{net_name}' ...")
                res = ""
                # Check if peer is online
                ping = conn.ping(machine)
                if ping is None:
                    res = "not reachable"
                    log.info(f"{machine} ({net_name}): {res}")
                else:
                    res = f"reachable, ping: {ping:.2f} ms"
                    log.info(f"{machine} ({net_name}): {res}")
                    break

    if not found:
        msg = f"Machine '{machine}' not found in any network"
        raise ClanError(msg)


def register_ping_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        type=str,
        help="Machine name to ping",
    )

    parser.add_argument(
        "--network",
        "-n",
        type=str,
        help="Specific network to use for ping (if not specified, checks all networks)",
    )

    parser.set_defaults(func=ping_command)
