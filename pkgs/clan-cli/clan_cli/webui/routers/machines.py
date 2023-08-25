from typing import Annotated

from fastapi import APIRouter, Body

from ...config.machine import schema_for_machine
from ...machines.create import create_machine as _create_machine
from ...machines.list import list_machines as _list_machines
from ..schemas import (
    Config,
    ConfigResponse,
    Machine,
    MachineCreate,
    MachineResponse,
    MachinesResponse,
    SchemaResponse,
    Status,
)

router = APIRouter()


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
    schema = schema_for_machine(name)
    return SchemaResponse(schema=schema)
