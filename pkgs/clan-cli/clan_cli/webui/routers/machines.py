# Logging setup
import logging
from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from clan_cli.webui.api_errors import MissingClanImports
from clan_cli.webui.api_inputs import MachineConfig

from ...config.machine import (
    config_for_machine,
    set_config_for_machine,
    verify_machine_config,
)
from ...config.schema import machine_schema
from ...machines.list import list_machines as _list_machines
from ...types import FlakeName
from ..api_outputs import (
    ConfigResponse,
    Machine,
    MachineResponse,
    MachinesResponse,
    SchemaResponse,
    Status,
    VerifyMachineResponse,
)
from ..tags import Tags

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/{flake_name}/machines", tags=[Tags.machine])
async def list_machines(flake_name: FlakeName) -> MachinesResponse:
    machines = []
    for m in _list_machines(flake_name):
        machines.append(Machine(name=m, status=Status.UNKNOWN))

    return MachinesResponse(machines=machines)


@router.get("/api/{flake_name}/machines/{name}", tags=[Tags.machine])
async def get_machine(flake_name: FlakeName, name: str) -> MachineResponse:
    log.error("TODO")
    return MachineResponse(machine=Machine(name=name, status=Status.UNKNOWN))


@router.get("/api/{flake_name}/machines/{name}/config", tags=[Tags.machine])
async def get_machine_config(flake_name: FlakeName, name: str) -> ConfigResponse:
    config = config_for_machine(flake_name, name)
    return ConfigResponse(**config)


@router.put("/api/{flake_name}/machines/{name}/config", tags=[Tags.machine])
async def put_machine(
    flake_name: FlakeName, name: str, config: Annotated[MachineConfig, Body()]
) -> None:
    """
    Set the config for a machine.
    Creates the machine if it doesn't yet exist.
    """
    conf = jsonable_encoder(config)
    set_config_for_machine(flake_name, name, conf)


@router.put(
    "/api/{flake_name}/schema",
    tags=[Tags.machine],
    responses={400: {"model": MissingClanImports}},
)
async def get_machine_schema(
    flake_name: FlakeName, config: Annotated[MachineConfig, Body()]
) -> SchemaResponse:
    schema = machine_schema(flake_name, config=dict(config))
    return SchemaResponse(schema=schema)


@router.get("/api/{flake_name}/machines/{name}/verify", tags=[Tags.machine])
async def get_verify_machine_config(
    flake_name: FlakeName, name: str
) -> VerifyMachineResponse:
    error = verify_machine_config(flake_name, name)
    success = error is None
    return VerifyMachineResponse(success=success, error=error)


@router.put("/api/{flake_name}/machines/{name}/verify", tags=[Tags.machine])
async def put_verify_machine_config(
    flake_name: FlakeName,
    name: str,
    config: Annotated[dict, Body()],
) -> VerifyMachineResponse:
    error = verify_machine_config(flake_name, name, config)
    success = error is None
    return VerifyMachineResponse(success=success, error=error)
