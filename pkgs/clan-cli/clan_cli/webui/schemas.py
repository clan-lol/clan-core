from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Status(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class Machine(BaseModel):
    name: str
    status: Status


class MachineCreate(BaseModel):
    name: str


class MachinesResponse(BaseModel):
    machines: list[Machine]


class MachineResponse(BaseModel):
    machine: Machine


class ConfigResponse(BaseModel):
    config: dict


class SchemaResponse(BaseModel):
    schema_: dict = Field(alias="schema")


class VmConfig(BaseModel):
    flake_url: str
    flake_attr: str

    cores: int
    memory_size: int
    graphics: bool


class VmStatusResponse(BaseModel):
    status: int
    running: bool


class VmCreateResponse(BaseModel):
    uuid: str


class VmInspectResponse(BaseModel):
    config: VmConfig


class FlakeAction(BaseModel):
    id: str
    uri: str


class FlakeResponse(BaseModel):
    content: str
    actions: List[FlakeAction]
