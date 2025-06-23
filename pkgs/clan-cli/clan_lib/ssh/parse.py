import re
import urllib.parse
from typing import TYPE_CHECKING

from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from clan_lib.ssh.remote import Remote


def parse_ssh_uri(
    *,
    machine_name: str,
    address: str,
) -> "Remote":
    """
    Parses an SSH URI into a Remote object.
    The address can be in the form of:
    - `ssh://[user@]hostname[:port]?option=value&option2=value2`
    - `[user@]hostname[:port]`
    The specification can be found here: https://www.ietf.org/archive/id/draft-salowey-secsh-uri-00.html
    """
    if address.startswith("ssh://"):
        # Strip the `ssh://` prefix if it exists
        address = address[len("ssh://") :]

    parts = address.split("?", maxsplit=1)
    endpoint, maybe_options = parts if len(parts) == 2 else (parts[0], "")

    parts = endpoint.split("@")
    match len(parts):
        case 2:
            user, host_port = parts
        case 1:
            user, host_port = "root", parts[0]
        case _:
            msg = f"Invalid host, got `{address}` but expected something like `[user@]hostname[:port]`"
            raise ClanError(msg)

    # Make this check now rather than failing with a `ValueError`
    # when looking up the port from the `urlsplit` result below:
    if host_port.count(":") > 1 and not re.match(r".*\[.*]", host_port):
        msg = f"Invalid hostname: {address}. IPv6 addresses must be enclosed in brackets , e.g. [::1]"
        raise ClanError(msg)

    options: dict[str, str] = {}
    for o in maybe_options.split("&"):
        if len(o) == 0:
            continue
        parts = o.split("=", maxsplit=1)
        if len(parts) != 2:
            msg = (
                f"Invalid option in host `{address}`: option `{o}` does not have "
                f"a value (i.e. expected something like `name=value`)"
            )
            raise ClanError(msg)
        name, value = parts
        options[name] = value

    result = urllib.parse.urlsplit(f"//{host_port}")
    if not result.hostname:
        msg = f"Invalid host, got `{address}` but expected something like `[user@]hostname[:port]`"
        raise ClanError(msg)
    hostname = result.hostname
    port = result.port
    from clan_lib.ssh.remote import Remote

    return Remote(
        address=hostname,
        user=user,
        port=port,
        command_prefix=machine_name,
        ssh_options=options,
    )
