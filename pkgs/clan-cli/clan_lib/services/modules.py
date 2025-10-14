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
    InventoryInstancesType,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.path_utils import get_value_by_path, set_value_by_path


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
            "Desktop": {"color": "#F4eeaa", "description": "Desktop Environment"},
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
    def from_dict(cls, data: dict[str, Any]) -> "ModuleManifest":
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


@dataclass(frozen=True, eq=True)
class Role:
    name: str
    description: str | None = None


@dataclass
class ModuleInfo:
    manifest: ModuleManifest
    roles: dict[str, Role]


@dataclass
class Module:
    # To use this module specify: InventoryInstanceModule :: { input, name } (foreign key)
    usage_ref: InventoryInstanceModule
    info: ModuleInfo
    native: bool
    instance_refs: list[str]


@dataclass
class ClanModules:
    modules: list[Module]
    core_input_name: str


def find_instance_refs_for_module(
    instances: InventoryInstancesType,
    module_ref: InventoryInstanceModule,
    core_input_name: str,
) -> list[str]:
    """Find all usages of a given module by its module_ref

    If the module is native:
        module_ref.input := None
        <instance>.module.name := None

    If module is from explicit input
        <instance>.module.name != None
        module_ref.input could be None, if explicit input refers to a native module

    """
    res: list[str] = []
    for instance_name, instance in instances.items():
        local_ref = instance.get("module")
        if not local_ref:
            continue

        local_name: str = local_ref.get("name", instance_name)
        local_input: str | None = local_ref.get("input")

        # Normal match
        if (
            local_name == module_ref.get("name")
            and local_input == module_ref.get("input")
        ) or (local_input == core_input_name and local_name == module_ref.get("name")):
            res.append(instance_name)

    return res


@API.register
def list_service_modules(flake: Flake) -> ClanModules:
    """Show information about a module"""
    # inputName.moduleName -> ModuleInfo
    modules: dict[str, dict[str, Any]] = flake.select(
        "clanInternals.inventoryClass.modulesPerSource"
    )

    # moduleName -> ModuleInfo
    builtin_modules: dict[str, Any] = flake.select(
        "clanInternals.inventoryClass.staticModules"
    )
    inventory_store = InventoryStore(flake)
    instances = inventory_store.read().get("instances", {})

    first_name, first_module = next(iter(builtin_modules.items()))
    clan_input_name = None
    for input_name, module_set in modules.items():
        if first_name in module_set:
            # Compare the manifest name
            module_set[first_name]["manifest"]["name"] = first_module["manifest"][
                "name"
            ]
            clan_input_name = input_name
            break

    if clan_input_name is None:
        msg = "Could not determine the clan-core input name"
        raise ClanError(msg)

    res: list[Module] = []
    for input_name, module_set in modules.items():
        for module_name, module_info in module_set.items():
            module_ref = InventoryInstanceModule(
                {
                    "name": module_name,
                    "input": None if input_name == clan_input_name else input_name,
                }
            )

            roles = module_info.get("roles", {})

            res.append(
                Module(
                    instance_refs=find_instance_refs_for_module(
                        instances, module_ref, clan_input_name
                    ),
                    usage_ref=module_ref,
                    info=ModuleInfo(
                        roles={
                            rname: Role(
                                name=rname,
                                description=roles[rname].get("description", None),
                            )
                            for rname in roles
                        },
                        manifest=ModuleManifest.from_dict(module_info["manifest"]),
                    ),
                    native=(input_name == clan_input_name),
                )
            )

    return ClanModules(res, clan_input_name)


def resolve_service_module_ref(
    flake: Flake,
    module_ref: InventoryInstanceModuleType,
) -> Module:
    """Checks if the module reference is valid

    :param module_ref: The module reference to check
    :raises ClanError: If the module_ref is invalid or missing required fields
    """
    service_modules = list_service_modules(flake)
    avilable_modules = service_modules.modules

    input_ref = module_ref.get("input", None)

    if input_ref is None or input_ref == service_modules.core_input_name:
        # Take only the native modules
        module_set = [m for m in avilable_modules if m.native]
    else:
        # Match the input ref
        module_set = [
            m for m in avilable_modules if m.usage_ref.get("input", None) == input_ref
        ]

    if not module_set:
        inputs = {m.usage_ref.get("input") for m in avilable_modules}
        msg = f"module set for input '{input_ref}' not found"
        msg += f"\nAvilable input_refs: {inputs}"
        msg += "\nOmit the input field to use the built-in modules\n"
        msg += "\n".join([m.usage_ref["name"] for m in avilable_modules if m.native])
        raise ClanError(msg)

    module_name = module_ref.get("name")
    if not module_name:
        msg = "Module name is required in module_ref"
        raise ClanError(msg)

    module = next((m for m in module_set if m.usage_ref["name"] == module_name), None)
    if module is None:
        msg = f"module with name '{module_name}' not found"
        raise ClanError(msg)

    return module


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
    input_name, module_name = module_ref.get("input"), module_ref["name"]
    module = resolve_service_module_ref(flake, module_ref)

    if module is None:
        msg = f"Module '{module_name}' not found in input '{input_name}'"
        raise ClanError(msg)

    if input_name is None:
        msg = "Not implemented for: input_name is None"
        raise ClanError(msg)

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
    input_name, module_name = module_ref.get("input"), module_ref["name"]
    module = resolve_service_module_ref(flake, module_ref)

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

    allowed_roles = module.info.roles
    for role_name, role_members in roles.items():
        if role_name not in allowed_roles:
            msg = f"Role '{role_name}' is not defined in the module"
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
    if not input_name:
        new_instance: InventoryInstance = {
            "module": {
                "name": module_name,
            },
            "roles": roles,
        }
    else:
        new_instance = {
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


@dataclass
class InventoryInstanceInfo:
    resolved: Module
    module: InventoryInstanceModule
    roles: InventoryInstanceRolesType


@API.register
def list_service_instances(flake: Flake) -> dict[str, InventoryInstanceInfo]:
    """Returns all currently present service instances including their full configuration"""
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    instances = inventory.get("instances", {})
    res: dict[str, InventoryInstanceInfo] = {}
    for instance_name, instance in instances.items():
        persisted_ref = instance.get("module", {"name": instance_name})
        module = resolve_service_module_ref(flake, persisted_ref)

        if module is None:
            msg = f"Module for instance '{instance_name}' not found"
            raise ClanError(msg)
        res[instance_name] = InventoryInstanceInfo(
            resolved=module,
            module=persisted_ref,
            roles=instance.get("roles", {}),
        )
    return res


@API.register
def set_service_instance(
    flake: Flake, instance_ref: str, roles: InventoryInstanceRolesType
) -> None:
    """Update the roles of a service instance

    :param instance_ref: The name of the instance to update
    :param roles: The roles to update


    :raises ClanError: If the instance_ref is invalid or missing required fields
    """
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    instance: InventoryInstance | None = get_value_by_path(
        inventory, f"instances.{instance_ref}", None
    )

    if instance is None:
        msg = f"Instance '{instance_ref}' not found"
        raise ClanError(msg)

    module_ref = instance.get("module")
    if module_ref is None:
        msg = f"Instance '{instance_ref}' seems invalid: Missing module reference"
        raise ClanError(msg)

    module = resolve_service_module_ref(flake, module_ref)

    allowed_roles = list(module.info.roles)

    for role_name in roles:
        if role_name not in allowed_roles:
            msg = f"Role '{role_name}' cannot be used in the module"
            description = f"Allowed roles: {', '.join(allowed_roles)}"
            raise ClanError(msg, description=description)

    for role_name, role_cfg in roles.items():
        if forbidden_keys := {"extraModules"} & role_cfg.keys():
            msg = f"Role '{role_name}' cannot contain {', '.join(f"'{k}'" for k in forbidden_keys)} directly"
            raise ClanError(msg)

        static = get_value_by_path(
            instance, f"roles.{role_name}", {}, expected_type=InventoryInstanceRolesType
        )

        # override settings, machines only if passed
        merged = {
            **static,
            **role_cfg,
        }

        set_value_by_path(
            inventory, f"instances.{instance_ref}.roles.{role_name}", merged
        )

    inventory_store.write(
        inventory, message=f"Update service instance '{instance_ref}'"
    )
