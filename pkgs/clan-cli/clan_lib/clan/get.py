from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix_models.clan import InventoryMeta
from clan_lib.persist.inventory_store import InventoryStore


@API.register
def get_clan_details(flake: Flake) -> InventoryMeta:
    if flake.is_local and not flake.path.exists():
        msg = f"Path {flake} does not exist"
        raise ClanError(msg, description="clan directory does not exist")
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    meta = inventory.get("meta")
    if not meta:
        msg = f"Inventory of flake '{flake}' does not have a meta attribute"
        raise ClanError(msg)

    return meta
