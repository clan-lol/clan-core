import logging

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import FieldSchema
from clan_lib.nix_models.clan import InventoryMeta
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import is_writeable_key, retrieve_typed_field_names

log = logging.getLogger(__name__)


@API.register
def get_clan_details(flake: Flake) -> InventoryMeta:
    """Retrieve the clan details from the inventory of a given flake.

    Args:
        flake: The Flake instance representing the clan.

    Returns:
        InventoryMeta: The meta information from the clan's inventory.

    Raises:
        ClanError: If the flake does not exist, or if the inventory is invalid (missing the meta attribute).

    """
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    meta = inventory.get("meta")
    if not meta:
        msg = f"Inventory of flake '{flake}' does not have a meta attribute"
        raise ClanError(msg)

    return meta


@API.register
def get_clan_details_schema(flake: Flake) -> dict[str, FieldSchema]:
    """
    Get attributes for each field of the clan.

    This function checks which fields of the 'clan' resource are readonly and provides a reason if so.

    Args:
        flake (Flake): The Flake object for which to retrieve fields.

    Returns:
        dict[str, FieldSchema]: A map from field-names to { 'readonly' (bool) and 'reason' (str or None ) }
    """

    inventory_store = InventoryStore(flake)
    write_info = inventory_store.get_writeability()

    field_names = retrieve_typed_field_names(InventoryMeta)

    return {
        field: {
            "readonly": not is_writeable_key(f"meta.{field}", write_info),
            # TODO: Provide a meaningful reason
            "reason": None,
            "readonly_members": [],
        }
        for field in field_names
    }
