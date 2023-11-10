import logging
import re
from pathlib import Path
from typing import Any

from pydantic import AnyUrl, BaseModel, Extra, validator

from ..dirs import clan_flakes_dir
from ..flakes.create import DEFAULT_URL
from ..types import validate_path

log = logging.getLogger(__name__)


class ClanFlakePath(BaseModel):
    flake_name: Path

    @validator("flake_name")
    def check_flake_name(cls: Any, v: Path) -> Path:  # noqa
        return validate_path(clan_flakes_dir(), v)


class FlakeCreateInput(ClanFlakePath):
    url: AnyUrl = DEFAULT_URL


class MachineConfig(BaseModel):
    clanImports: list[str] = []  # noqa: N815
    clan: dict = {}

    # allow extra fields to cover the full spectrum of a nixos config
    class Config:
        extra = Extra.allow


class MachineCreate(BaseModel):
    name: str

    @classmethod
    @validator("name")
    def validate_hostname(cls, v: str) -> str:
        hostname_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
        if not re.match(hostname_regex, v):
            raise ValueError("Machine name must be a valid hostname")
        return v
