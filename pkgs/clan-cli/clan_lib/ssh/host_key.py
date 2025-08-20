# Adapted from https://github.com/numtide/deploykit

from typing import Literal

from clan_lib.errors import ClanError

HostKeyCheck = Literal[
    "strict",  # Strictly check ssh host keys, prompt for unknown ones
    "ask",  # Ask for confirmation on first use
    "accept-new",  # Trust on ssh keys on first use
    "none",  # Do not check ssh host keys
]


def hostkey_to_ssh_opts(host_key_check: HostKeyCheck) -> list[str]:
    """Convert a HostKeyCheck value to SSH options."""
    match host_key_check:
        case "strict":
            return ["-o", "StrictHostKeyChecking=yes"]
        case "ask":
            return []
        case "accept-new" | "tofu":
            return ["-o", "StrictHostKeyChecking=accept-new"]
        case "none":
            return [
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
            ]
        case _:
            msg = f"Invalid HostKeyCheck: {host_key_check}"
            raise ClanError(msg)
