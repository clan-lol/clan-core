# Logging setup
import logging
from pathlib import Path
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


@router.get("/api/machines", tags=[Tags.machine])
async def list_machines(flake_dir: Path) -> MachinesResponse:
    machines = []
    for m in _list_machines(flake_dir):
        machines.append(Machine(name=m, status=Status.UNKNOWN))

    return MachinesResponse(machines=machines)


@router.get("/api/machines/{name}", tags=[Tags.machine])
async def get_machine(flake_dir: Path, name: str) -> MachineResponse:
    log.error("TODO")
    return MachineResponse(machine=Machine(name=name, status=Status.UNKNOWN))


@router.get("/api/machines/{name}/config", tags=[Tags.machine])
async def get_machine_config(flake_dir: Path, name: str) -> ConfigResponse:
    config = config_for_machine(flake_dir, name)
    return ConfigResponse(**config)


@router.put("/api/machines/{name}/config", tags=[Tags.machine])
async def set_machine_config(
    flake_dir: Path, name: str, config: Annotated[MachineConfig, Body()]
) -> None:
    conf = jsonable_encoder(config)
    set_config_for_machine(flake_dir, name, conf)


@router.put(
    "/api/schema",
    tags=[Tags.machine],
    responses={400: {"model": MissingClanImports}},
)
async def get_machine_schema(
    flake_dir: Path, config: Annotated[dict, Body()]
) -> SchemaResponse:
    schema = machine_schema(flake_dir, config=config)
    return SchemaResponse(schema=schema)


@router.get("/api/machines/{name}/verify", tags=[Tags.machine])
async def get_verify_machine_config(
    flake_dir: Path, name: str
) -> VerifyMachineResponse:
    error = verify_machine_config(flake_dir, name)
    success = error is None
    return VerifyMachineResponse(success=success, error=error)


@router.put("/api/machines/{name}/verify", tags=[Tags.machine])
async def put_verify_machine_config(
    flake_dir: Path,
    name: str,
    config: Annotated[dict, Body()],
) -> VerifyMachineResponse:
    error = verify_machine_config(flake_dir, name, config)
    success = error is None
    return VerifyMachineResponse(success=success, error=error)
