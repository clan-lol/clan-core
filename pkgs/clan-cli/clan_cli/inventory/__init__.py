import json
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Literal

from clan_cli.errors import ClanError
from clan_cli.git import commit_file


def sanitize_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def dataclass_to_dict(obj: Any) -> Any:
    """
    Utility function to convert dataclasses to dictionaries
    It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

    It does NOT convert member functions.
    """
    if is_dataclass(obj):
        return {
            sanitize_string(k): dataclass_to_dict(v)
            for k, v in asdict(obj).items()  # type: ignore
        }
    elif isinstance(obj, list | tuple):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {sanitize_string(k): dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, str):
        return sanitize_string(obj)
    else:
        return obj


@dataclass
class Machine:
    """
    Inventory machine model.

    DO NOT EDIT THIS CLASS.
    Any changes here must be reflected in the inventory interface file and potentially other nix files.

    - Persisted to the inventory.json file
    - Source of truth to generate each clan machine.
    - For hardware deployment, the machine must declare the host system.
    """

    name: str
    system: Literal["x86_64-linux"] | str | None = None
    description: str | None = None
    icon: str | None = None
    tags: list[str] = field(default_factory=list)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Machine":
        return Machine(**d)


@dataclass
class MachineServiceConfig:
    config: dict[str, Any] | None = None


@dataclass
class ServiceMeta:
    name: str
    description: str | None = None
    icon: str | None = None


@dataclass
class Role:
    machines: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class Service:
    meta: ServiceMeta
    roles: dict[str, Role]
    machines: dict[str, MachineServiceConfig] = field(default_factory=dict)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Service":
        return Service(
            meta=ServiceMeta(**d.get("meta", {})),
            roles={name: Role(**role) for name, role in d.get("roles", {}).items()},
            machines=(
                {
                    name: MachineServiceConfig(**machine)
                    for name, machine in d.get("machines", {}).items()
                }
                if d.get("machines")
                else {}
            ),
        )


@dataclass
class InventoryMeta:
    name: str
    description: str | None = None
    icon: str | None = None


@dataclass
class Inventory:
    meta: InventoryMeta
    machines: dict[str, Machine]
    services: dict[str, dict[str, Service]]

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Inventory":
        return Inventory(
            meta=InventoryMeta(**d.get("meta", {})),
            machines={
                name: Machine.from_dict(machine)
                for name, machine in d.get("machines", {}).items()
            },
            services={
                name: {
                    role: Service.from_dict(service)
                    for role, service in services.items()
                }
                for name, services in d.get("services", {}).items()
            },
        )

    @staticmethod
    def get_path(flake_dir: str | Path) -> Path:
        return Path(flake_dir) / "inventory.json"

    @staticmethod
    def load_file(flake_dir: str | Path) -> "Inventory":
        inventory = Inventory(
            machines={}, services={}, meta=InventoryMeta(name="New Clan")
        )
        inventory_file = Inventory.get_path(flake_dir)
        if inventory_file.exists():
            with open(inventory_file) as f:
                try:
                    res = json.load(f)
                    inventory = Inventory.from_dict(res)
                except json.JSONDecodeError as e:
                    raise ClanError(f"Error decoding inventory file: {e}")

        return inventory

    def persist(self, flake_dir: str | Path, message: str) -> None:
        inventory_file = Inventory.get_path(flake_dir)

        with open(inventory_file, "w") as f:
            json.dump(dataclass_to_dict(self), f, indent=2)

        commit_file(inventory_file, Path(flake_dir), commit_message=message)
