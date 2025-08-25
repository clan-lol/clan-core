import re
import tomllib
from dataclasses import dataclass, field, fields
from typing import Any, TypedDict, TypeVar

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.clan import (
    InventoryInstance,
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
    - readme_content (str): The content of the README file as a string.

    Returns
    -------
    - str: The extracted frontmatter as a string.
    - str: The content of the README file without the frontmatter.

    Raises
    ------
    - ValueError: If the README does not contain valid frontmatter.

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


class ModuleList(TypedDict):
    modules: dict[str, dict[str, ModuleInfo]]


@API.register
def list_service_modules(flake: Flake) -> ModuleList:
    """Show information about a module"""
    modules = flake.select("clanInternals.inventoryClass.modulesPerSource")

    res: dict[str, dict[str, ModuleInfo]] = {}
    for input_name, module_set in modules.items():
        res[input_name] = {}

        for module_name, module_info in module_set.items():
            # breakpoint()
            res[input_name][module_name] = ModuleInfo(
                manifest=ModuleManifest.from_dict(module_info.get("manifest")),
                roles=module_info.get("roles", {}),
            )

    return ModuleList(modules=res)


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
    module_set = avilable_modules.get("modules", {}).get(input_name)

    assert module_set is not None  # Since check_service_module_ref already checks this

    module = module_set.get(module_name)

    assert module is not None  # Since check_service_module_ref already checks this

    return module


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

    module_set = avilable_modules.get("modules", {}).get(input_ref)

    if module_set is None:
        msg = f"module set for input '{input_ref}' not found"
        msg += f"\nAvilable input_refs: {avilable_modules.get('modules', {}).keys()}"
        raise ClanError(msg)

    module_name = module_ref.get("name")
    assert module_name
    module = module_set.get(module_name)
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

    # TODO: Check the roles against the schema
    schema = get_service_module_schema(flake, module_ref)
    for role_name in roles:
        if role_name not in schema:
            msg = f"Role '{role_name}' is not defined in the module schema"
            raise ClanError(msg)

    # TODO: Validate roles against the schema

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
