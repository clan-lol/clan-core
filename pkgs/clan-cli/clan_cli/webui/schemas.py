from enum import Enum

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


class Config(BaseModel):
    pass


class ConfigResponse(BaseModel):
    config: Config


class Schema(BaseModel):
    pass


class SchemaResponse(BaseModel):
    schema_: Schema = Field(alias="schema")
