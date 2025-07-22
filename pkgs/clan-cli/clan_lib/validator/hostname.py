import re

from clan_lib.errors import ClanError


def hostname(host: str) -> str:
    """
    Validates a hostname according to the expected format in NixOS.

    Usage Example

    @dataclass
    class Clan:
        name: str

        def validate(self) -> None:
            from clan_lib.validator.hostname import hostname
            try:
                hostname(self.name)
            except ValueError as e:
                raise ClanError(str(e), location="name")
    """

    # TODO: Generate from nix schema
    hostname_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
    if not re.fullmatch(hostname_regex, host):
        msg = "Machine name must be a valid hostname"
        raise ClanError(msg, location="Create Machine")

    return host
