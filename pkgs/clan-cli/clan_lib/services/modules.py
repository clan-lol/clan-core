import re
import tomllib
from dataclasses import dataclass, field, fields
from typing import Any, TypedDict, TypeVar

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.clan import (
    InventoryInstance,
    InventoryInstanceModule,
    InventoryInstanceModuleType,
    InventoryInstanceRolesType,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path


class CategoryInfo(TypedDict):
    color: str
    description: str


@dataclass
class ModuleManifest:
    name: str
    description: str
    categories: list[str] = field(default_factory=lambda: ["Uncategorized"])
    features: list[str] = field(default_factory=list)

    @classmethod
    def categories_info(cls) -> dict[str, CategoryInfo]:
        category_map: dict[str, CategoryInfo] = {
            "AudioVideo": {
                "color": "#AEC6CF",
                "description": "Applications for presenting, creating, or processing multimedia (audio/video)",
            },
            "Audio": {"color": "#CFCFC4", "description": "Audio"},
            "Video": {"color": "#FFD1DC", "description": "Video"},
            "Development": {"color": "#F49AC2", "description": "Development"},
            "Education": {"color": "#B39EB5", "description": "Education"},
            "Game": {"color": "#FFB347", "description": "Game"},
            "Graphics": {"color": "#FF6961", "description": "Graphics"},
            "Social": {"color": "#76D7C4", "description": "Social"},
            "Network": {"color": "#77DD77", "description": "Network"},
            "Office": {"color": "#85C1E9", "description": "Office"},
            "Science": {"color": "#779ECB", "description": "Science"},
            "System": {"color": "#F5C3C0", "description": "System"},
            "Settings": {"color": "#03C03C", "description": "Settings"},
            "Utility": {"color": "#B19CD9", "description": "Utility"},
            "Uncategorized": {"color": "#C23B22", "description": "Uncategorized"},
        }

        return category_map

    def __post_init__(self) -> None:
        for category in self.categories:
            if category not in ModuleManifest.categories_info():
                msg = f"Invalid category: {category}"
                raise ValueError(msg)

    @classmethod
    def from_dict(cls, data: dict) -> "ModuleManifest":
        """Create an instance of this class from a dictionary.
        Drops any keys that are not defined in the dataclass.
        """
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})


def parse_frontmatter(readme_content: str) -> tuple[dict[str, Any] | None, str]:
    """Extracts TOML frontmatter from a string

    Raises:
    - ClanError: If the toml frontmatter is invalid

    """
    # Pattern to match YAML frontmatter enclosed by triple-dashed lines
    frontmatter_pattern = r"^---\s+(.*?)\s+---\s?+(.*)$"

    # Search for the frontmatter using the pattern
    match = re.search(frontmatter_pattern, readme_content, re.DOTALL)

    # If a match is found, return the frontmatter content
    match = re.search(frontmatter_pattern, readme_content, re.DOTALL)

    # If a match is found, parse the TOML frontmatter and return both parts
    if match:
        frontmatter_raw, remaining_content = match.groups()
        try:
            # Parse the TOML frontmatter
            frontmatter_parsed = tomllib.loads(frontmatter_raw)
        except tomllib.TOMLDecodeError as e:
            msg = f"Error parsing TOML frontmatter: {e}"
            raise ClanError(
                msg,
                description="Invalid TOML frontmatter",
                location="parse_frontmatter",
            ) from e

        return frontmatter_parsed, remaining_content
    return None, readme_content


T = TypeVar("T")


def extract_frontmatter[T](
    readme_content: str,
    err_scope: str,
    fm_class: type[T],
) -> tuple[T, str]:
    """Extracts TOML frontmatter from a README file content.

    Parameters
    ----------
    readme_content : str
        The content of the README file as a string.
    err_scope : str
        The error scope for error messages.
    fm_class : type[T]
        The class type to deserialize the frontmatter into.

    Returns
    -------
    tuple[T, str]
        The extracted frontmatter object and the content without frontmatter.

    Raises
    ------
    ClanError
        If the README does not contain valid frontmatter.

    """
    frontmatter_raw, remaining_content = parse_frontmatter(readme_content)

    if frontmatter_raw:
        return fm_class(**frontmatter_raw), remaining_content

    # If no frontmatter is found, raise an error
    msg = "Invalid README: Frontmatter not found."
    raise ClanError(
        msg,
        location="extract_module_frontmatter",
        description=f"{err_scope} does not contain valid frontmatter.",
    )


@dataclass
class ModuleInfo(TypedDict):
    manifest: ModuleManifest
    roles: dict[str, None]


class Module(TypedDict):
    module: InventoryInstanceModule
    info: ModuleInfo


@API.register
def list_service_modules(flake: Flake) -> list[Module]:
    """Show information about a module"""
    modules = flake.select("clanInternals.inventoryClass.modulesPerSource")

    if "clan-core" not in modules:
        msg = "Cannot find 'clan-core' input in the flake. Make sure your clan-core input is named 'clan-core'"
        raise ClanError(msg)

    res: list[Module] = []
    for input_name, module_set in modules.items():
        for module_name, module_info in module_set.items():
            res.append(
                Module(
                    module={"name": module_name, "input": input_name},
                    info=ModuleInfo(
                        manifest=ModuleManifest.from_dict(
                            module_info.get("manifest"),
                        ),
                        roles=module_info.get("roles", {}),
                    ),
                )
            )

    return res


@API.register
def get_service_module(
    flake: Flake,
    module_ref: InventoryInstanceModuleType,
) -> ModuleInfo:
    """Returns the module information for a given module reference

    :param module_ref: The module reference to get the information for
    :return: Dict of module information
    :raises ClanError: If the module_ref is invalid or missing required fields
    """
    input_name, module_name = check_service_module_ref(flake, module_ref)

    avilable_modules = list_service_modules(flake)
    module_set: list[Module] = [
        m for m in avilable_modules if m["module"].get("input", None) == input_name
    ]

    if not module_set:
        msg = f"Module set for input '{input_name}' not found"
        raise ClanError(msg)

    module = next((m for m in module_set if m["module"]["name"] == module_name), None)

    if module is None:
        msg = f"Module '{module_name}' not found in input '{input_name}'"
        raise ClanError(msg)

    return module["info"]


def check_service_module_ref(
    flake: Flake,
    module_ref: InventoryInstanceModuleType,
) -> tuple[str, str]:
    """Checks if the module reference is valid

    :param module_ref: The module reference to check
    :raises ClanError: If the module_ref is invalid or missing required fields
    """
    avilable_modules = list_service_modules(flake)

    input_ref = module_ref.get("input", None)
    if input_ref is None:
        msg = "Setting module_ref.input is currently required"
        raise ClanError(msg)

    module_set = [
        m for m in avilable_modules if m["module"].get("input", None) == input_ref
    ]

    if module_set is None:
        inputs = {m["module"].get("input") for m in avilable_modules}
        msg = f"module set for input '{input_ref}' not found"
        msg += f"\nAvilable input_refs: {inputs}"
        raise ClanError(msg)

    module_name = module_ref.get("name")
    if not module_name:
        msg = "Module name is required in module_ref"
        raise ClanError(msg)
    module = next((m for m in module_set if m["module"]["name"] == module_name), None)
    if module is None:
        msg = f"module with name '{module_name}' not found"
        raise ClanError(msg)

    return (input_ref, module_name)


@API.register
def get_service_module_schema(
    flake: Flake,
    module_ref: InventoryInstanceModuleType,
) -> dict[str, Any]:
    """Returns the schema for a service module

    :param module_ref: The module reference to get the schema for
    :return: Dict of schemas for the service module roles
    :raises ClanError: If the module_ref is invalid or missing required fields
    """
    input_name, module_name = check_service_module_ref(flake, module_ref)

    return flake.select(
        f"clanInternals.inventoryClass.moduleSchemas.{input_name}.{module_name}",
    )


@API.register
def create_service_instance(
    flake: Flake,
    module_ref: InventoryInstanceModuleType,
    roles: InventoryInstanceRolesType,
) -> None:
    """Show information about a module"""
    input_name, module_name = check_service_module_ref(flake, module_ref)

    inventory_store = InventoryStore(flake)

    inventory = inventory_store.read()

    # TODO: Multiple instances support
    instance_name = module_name
    curr_instances = inventory.get("instances", {})

    if instance_name in curr_instances:
        msg = f"Instance '{instance_name}' already exists in the inventory"
        raise ClanError(msg)

    if roles == {}:
        msg = "Creating a service instance requires adding roles"
        raise ClanError(msg)

    all_machines = inventory.get("machines", {})
    available_machine_refs = set(all_machines.keys())

    schema = get_service_module_schema(flake, module_ref)
    for role_name, role_members in roles.items():
        if role_name not in schema:
            msg = f"Role '{role_name}' is not defined in the module schema"
            raise ClanError(msg)

        machine_refs = role_members.get("machines")
        msg = f"Role: '{role_name}' - "
        if machine_refs:
            unavailable_machines = list(
                filter(lambda m: m not in available_machine_refs, machine_refs),
            )
            if unavailable_machines:
                msg += f"Unknown machine reference: {unavailable_machines}. Use one of {available_machine_refs}"
                raise ClanError(msg)

        # TODO: Check the settings against the schema
        # settings = role_members.get("settings", {})

    # Create a new instance with the given roles
    new_instance: InventoryInstance = {
        "module": {
            "name": module_name,
            "input": input_name,
        },
        "roles": roles,
    }

    set_value_by_path(inventory, f"instances.{instance_name}", new_instance)
    inventory_store.write(
        inventory,
        message=f"Add service instance '{instance_name}' with module '{module_name} from {input_name}'",
        commit=True,
    )


class InventoryInstanceInfo(TypedDict):
    module: Module
    roles: InventoryInstanceRolesType


@API.register
def list_service_instances(flake: Flake) -> dict[str, InventoryInstanceInfo]:
    """Returns all currently present service instances including their full configuration"""
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()
    service_modules = {
        (mod["module"]["name"], mod["module"].get("input", "clan-core")): mod
        for mod in list_service_modules(flake)
    }
    instances = inventory.get("instances", {})
    res: dict[str, InventoryInstanceInfo] = {}
    for instance_name, instance in instances.items():
        module_key = (
            instance.get("module", {})["name"],
            instance.get("module", {}).get("input")
            or "clan-core",  # Replace None (or falsey) with "clan-core"
        )
        module = service_modules.get(module_key)
        if module is None:
            msg = f"Module '{module_key}' for instance '{instance_name}' not found"
            raise ClanError(msg)
        res[instance_name] = InventoryInstanceInfo(
            module=module,
            roles=instance.get("roles", {}),
        )
    return res
