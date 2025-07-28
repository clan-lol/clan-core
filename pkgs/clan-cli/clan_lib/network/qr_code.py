import json
import logging
from pathlib import Path
from typing import Any

from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.network.network import Network, Peer
from clan_lib.nix import nix_shell
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


def parse_qr_json_to_networks(
    qr_data: dict[str, Any], flake: Flake
) -> dict[str, dict[str, Any]]:
    """
    Parse QR code JSON contents and output a dict of networks with remotes.

    Args:
        qr_data: JSON data from QR code containing network information
        flake: Flake instance for creating peers

    Returns:
        Dictionary mapping network type to dict with "network" and "remote" keys

    Example input:
        {
            "pass": "password123",
            "tor": "ssh://user@hostname.onion",
            "addrs": ["ssh://user@192.168.1.100", "ssh://user@example.com"]
        }

    Example output:
        {
            "direct": {
                "network": Network(...),
                "remote": Remote(...)
            },
            "tor": {
                "network": Network(...),
                "remote": Remote(...)
            }
        }
    """
    networks: dict[str, dict[str, Any]] = {}

    password = qr_data.get("pass")

    # Process clearnet addresses
    clearnet_addrs = qr_data.get("addrs", [])
    if clearnet_addrs:
        # For now, just use the first address
        addr = clearnet_addrs[0]
        if isinstance(addr, str):
            peer = Peer(name="installer", _host={"plain": addr}, flake=flake)
            network = Network(
                peers={"installer": peer},
                module_name="clan_lib.network.direct",
                priority=1000,
            )
            # Create the remote with password
            remote = Remote.from_ssh_uri(
                machine_name="installer",
                address=addr,
            ).override(password=password)

            networks["direct"] = {"network": network, "remote": remote}
        else:
            msg = f"Invalid address format: {addr}"
            raise ClanError(msg)

    # Process tor address
    if tor_addr := qr_data.get("tor"):
        peer = Peer(name="installer-tor", _host={"plain": tor_addr}, flake=flake)
        network = Network(
            peers={"installer-tor": peer},
            module_name="clan_lib.network.tor",
            priority=500,
        )
        # Create the remote with password and tor settings
        remote = Remote.from_ssh_uri(
            machine_name="installer-tor",
            address=tor_addr,
        ).override(password=password, socks_port=9050, socks_wrapper=["torify"])

        networks["tor"] = {"network": network, "remote": remote}

    return networks


def parse_qr_image_to_json(image_path: Path) -> dict[str, Any]:
    """
    Parse a QR code image and extract the JSON data.

    Args:
        image_path: Path to the QR code image file

    Returns:
        Parsed JSON data from the QR code

    Raises:
        ClanError: If the QR code cannot be read or contains invalid JSON
    """
    if not image_path.exists():
        msg = f"QR code image file not found: {image_path}"
        raise ClanError(msg)

    cmd = nix_shell(
        ["zbar"],
        [
            "zbarimg",
            "--quiet",
            "--raw",
            str(image_path),
        ],
    )

    try:
        res = run(cmd)
        data = res.stdout.strip()

        if not data:
            msg = f"No QR code found in image: {image_path}"
            raise ClanError(msg)

        return json.loads(data)
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON in QR code: {e}"
        raise ClanError(msg) from e
    except Exception as e:
        msg = f"Failed to read QR code from {image_path}: {e}"
        raise ClanError(msg) from e
