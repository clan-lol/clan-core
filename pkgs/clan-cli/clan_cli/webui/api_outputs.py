from enum import Enum

from pydantic import BaseModel, Extra, Field

from ..async_cmd import CmdOut
from ..task_manager import TaskStatus


class Status(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ClanModulesResponse(BaseModel):
    clan_modules: list[str]


class Machine(BaseModel):
    name: str
    status: Status


class MachinesResponse(BaseModel):
    machines: list[Machine]


class MachineResponse(BaseModel):
    machine: Machine


class ConfigResponse(BaseModel):
    clanImports: list[str] = []  # noqa: N815
    clan: dict = {}

    # allow extra fields to cover the full spectrum of a nixos config
    class Config:
        extra = Extra.allow


class SchemaResponse(BaseModel):
    schema_: dict = Field(alias="schema")


class VerifyMachineResponse(BaseModel):
    success: bool
    error: str | None


class VmStatusResponse(BaseModel):
    error: str | None
    status: TaskStatus


class VmCreateResponse(BaseModel):
    uuid: str


class FlakeAttrResponse(BaseModel):
    flake_attrs: list[str]


class FlakeAction(BaseModel):
    id: str
    uri: str


class FlakeListResponse(BaseModel):
    flakes: list[str]


class FlakeCreateResponse(BaseModel):
    cmd_out: dict[str, CmdOut]


class FlakeResponse(BaseModel):
    content: str
    actions: list[FlakeAction]
