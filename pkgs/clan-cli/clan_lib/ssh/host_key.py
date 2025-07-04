# Adapted from https://github.com/numtide/deploykit

from enum import Enum

from clan_lib.errors import ClanError


class HostKeyCheck(Enum):
    STRICT = "strict"  # Strictly check ssh host keys, prompt for unknown ones
    ASK = "ask"  # Ask for confirmation on first use
    TOFU = "tofu"  # Trust on ssh keys on first use
    NONE = "none"  # Do not check ssh host keys


def hostkey_to_ssh_opts(host_key_check: HostKeyCheck) -> list[str]:
    """
    Convert a HostKeyCheck value to SSH options.
    """
    match host_key_check:
        case HostKeyCheck.STRICT:
            return ["-o", "StrictHostKeyChecking=yes"]
        case HostKeyCheck.ASK:
            return []
        case HostKeyCheck.TOFU:
            return ["-o", "StrictHostKeyChecking=accept-new"]
        case HostKeyCheck.NONE:
            return [
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
            ]
        case _:
            msg = f"Invalid HostKeyCheck: {host_key_check}"
            raise ClanError(msg)
