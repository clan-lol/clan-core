# Logging setup
import logging
from typing import Annotated

from fastapi import APIRouter, Body

from ...config.machine import (
    config_for_machine,
    schema_for_machine,
    set_config_for_machine,
    verify_machine_config,
)
from ...machines.create import create_machine as _create_machine
from ...machines.list import list_machines as _list_machines
from ..api_outputs import (
    ConfigResponse,
    Machine,
    MachineCreate,
    MachineResponse,
    MachinesResponse,
    SchemaResponse,
    Status,
    VerifyMachineResponse,
)

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/machines")
async def list_machines() -> MachinesResponse:
    machines = []
    for m in _list_machines():
        machines.append(Machine(name=m, status=Status.UNKNOWN))
    return MachinesResponse(machines=machines)


@router.post("/api/machines", status_code=201)
async def create_machine(machine: Annotated[MachineCreate, Body()]) -> MachineResponse:
    out = await _create_machine(machine.name)
    log.debug(out)
    return MachineResponse(machine=Machine(name=machine.name, status=Status.UNKNOWN))


@router.get("/api/machines/{name}")
async def get_machine(name: str) -> MachineResponse:
    log.error("TODO")
    return MachineResponse(machine=Machine(name=name, status=Status.UNKNOWN))


@router.get("/api/machines/{name}/config")
async def get_machine_config(name: str) -> ConfigResponse:
    config = config_for_machine(name)
    return ConfigResponse(config=config)


@router.put("/api/machines/{name}/config")
async def set_machine_config(
    name: str, config: Annotated[dict, Body()]
) -> ConfigResponse:
    set_config_for_machine(name, config)
    return ConfigResponse(config=config)


@router.get("/api/machines/{name}/schema")
async def get_machine_schema(name: str) -> SchemaResponse:
    schema = schema_for_machine(name)
    return SchemaResponse(schema=schema)


@router.put("/api/machines/{name}/schema")
async def set_machine_schema(
    name: str, config: Annotated[dict, Body()]
) -> SchemaResponse:
    schema = schema_for_machine(name, config)
    return SchemaResponse(schema=schema)


@router.get("/api/machines/{name}/verify")
async def get_verify_machine_config(name: str) -> VerifyMachineResponse:
    error = verify_machine_config(name)
    success = error is None
    return VerifyMachineResponse(success=success, error=error)


@router.put("/api/machines/{name}/verify")
async def put_verify_machine_config(
    name: str,
    config: Annotated[dict, Body()],
) -> VerifyMachineResponse:
    error = verify_machine_config(name, config)
    success = error is None
    return VerifyMachineResponse(success=success, error=error)
