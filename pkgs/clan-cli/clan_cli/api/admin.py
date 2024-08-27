from clan_cli.api import API
from clan_cli.inventory import (
    AdminConfig,
    ServiceAdmin,
    ServiceAdminRole,
    ServiceAdminRoleDefault,
    ServiceMeta,
    load_inventory_eval,
    save_inventory,
)


@API.register
def get_admin_service(base_url: str) -> ServiceAdmin | None:
    """
    Return the admin service of a clan.

    There is only one admin service. This might be changed in the future
    """
    inventory = load_inventory_eval(base_url)
    return inventory.services.admin.get("admin")


@API.register
def set_admin_service(
    base_url: str, allowed_keys: list[str], instance_name: str = "admin"
) -> None:
    """
    Set the admin service of a clan
    Every machine is by default part of the admin service via the 'all' tag
    """
    inventory = load_inventory_eval(base_url)

    if not allowed_keys:
        raise ValueError("At least one key must be provided to ensure access")

    keys = []
    for keyfile in allowed_keys:
        if not keyfile.startswith("/"):
            raise ValueError(f"Keyfile '{keyfile}' must be an absolute path")
        with open(keyfile) as f:
            pubkey = f.read()
            keys.append(pubkey)

    instance = ServiceAdmin(
        meta=ServiceMeta(name=instance_name),
        roles=ServiceAdminRole(
            default=ServiceAdminRoleDefault(
                config=AdminConfig(allowedKeys=keys),
                machines=[],
                tags=["all"],
            )
        ),
    )

    inventory.services.admin[instance_name] = instance

    save_inventory(
        inventory,
        base_url,
        f"Set admin service: '{instance_name}'",
    )