import logging

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import Flake

log = logging.getLogger(__name__)


@API.register
def check_clan_valid(flake: Flake) -> bool:
    """Check if a clan is valid by verifying if it has the clanInternals attribute.
    Args:
        flake: The Flake instance representing the clan.
    Returns:
        bool: True if the clan exists, False otherwise.
    """
    try:
        flake.prefetch()
    except ClanError as e:
        msg = f"Flake {flake} is not valid: {e}"
        log.info(msg)
        return False

    if flake.is_local and not flake.path.exists():
        msg = f"Path {flake} does not exist"
        log.info(msg)
        return False

    try:
        flake.select("clanInternals.inventoryClass.directory")
    except ClanError as e:
        msg = f"Flake {flake} is not a valid clan directory: {e}"
        log.info(msg)
        return False

    return True
