import re
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Literal

from clan_cli.errors import ClanError


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
    tags: list[str] | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Machine":
        if "name" not in d:
            raise ClanError("name not found in machine")

        hostname_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
        if not re.match(hostname_regex, d["name"]):
            raise ClanError(
                "Machine name must be a valid hostname",
                description=f"""Machine name: {d["name"]}""",
            )

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
    machines: list[str] | None = None
    tags: list[str] | None = None


@dataclass
class Service:
    meta: ServiceMeta
    roles: dict[str, Role]
    machines: dict[str, MachineServiceConfig] | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Service":
        if "meta" not in d:
            raise ClanError("meta not found in service")

        if "roles" not in d:
            raise ClanError("roles not found in service")

        return Service(
            meta=ServiceMeta(**d["meta"]),
            roles={name: Role(**role) for name, role in d["roles"].items()},
            machines={
                name: MachineServiceConfig(**machine)
                for name, machine in d.get("machines", {}).items()
            },
        )


@dataclass
class Inventory:
    machines: dict[str, Machine]
    services: dict[str, dict[str, Service]]

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Inventory":
        if "machines" not in d:
            raise ClanError("machines not found in inventory")

        if "services" not in d:
            raise ClanError("services not found in inventory")

        return Inventory(
            machines={
                name: Machine.from_dict(machine)
                for name, machine in d["machines"].items()
            },
            services={
                name: {
                    role: Service.from_dict(service)
                    for role, service in services.items()
                }
                for name, services in d["services"].items()
            },
        )
