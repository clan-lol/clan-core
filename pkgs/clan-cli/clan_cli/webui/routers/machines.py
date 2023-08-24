from enum import Enum

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class Status(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class Machine(BaseModel):
    name: str
    status: Status


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
    return MachinesResponse(machines=[])


@router.get("/api/machines/{machine}")
async def get_machine(machine: str) -> MachineResponse:
    return MachineResponse(machine=Machine(name=machine, status=Status.ONLINE))


@router.get("/api/machines/{machine}/config")
async def get_machine_config(machine: str) -> ConfigResponse:
    return ConfigResponse(config=Config())


@router.post("/api/machines/{machine}/config")
async def set_machine_config(machine: str, config: Config) -> ConfigResponse:
    return ConfigResponse(config=config)


@router.get("/api/machines/{machine}/schema")
async def get_machine_schema(machine: str) -> SchemaResponse:
    return SchemaResponse(schema=Schema())
