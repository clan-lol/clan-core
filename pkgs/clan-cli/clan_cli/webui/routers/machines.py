from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

from ...machines.create import create_machine as _create_machine
from ...machines.list import list_machines as _list_machines

router = APIRouter()


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


@router.get("/api/machines")
async def list_machines() -> MachinesResponse:
    machines = []
    for m in _list_machines():
        machines.append(Machine(name=m, status=Status.UNKNOWN))
    return MachinesResponse(machines=machines)


@router.post("/api/machines", status_code=201)
async def create_machine(machine: Annotated[MachineCreate, Body()]) -> MachineResponse:
    _create_machine(machine.name)
    return MachineResponse(machine=Machine(name=machine.name, status=Status.UNKNOWN))


@router.get("/api/machines/{name}")
async def get_machine(name: str) -> MachineResponse:
    print("TODO")
    return MachineResponse(machine=Machine(name=name, status=Status.UNKNOWN))


@router.get("/api/machines/{name}/config")
async def get_machine_config(name: str) -> ConfigResponse:
    return ConfigResponse(config=Config())


@router.put("/api/machines/{name}/config")
async def set_machine_config(
    name: str, config: Annotated[Config, Body()]
) -> ConfigResponse:
    print("TODO")
    return ConfigResponse(config=config)


@router.get("/api/machines/{name}/schema")
async def get_machine_schema(name: str) -> SchemaResponse:
    print("TODO")
    return SchemaResponse(schema=Schema())
