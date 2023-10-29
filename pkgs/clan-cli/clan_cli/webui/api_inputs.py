import logging
from pathlib import Path
from typing import Any

from pydantic import AnyUrl, BaseModel, validator

from ..dirs import clan_data_dir, clan_flakes_dir
from ..flakes.create import DEFAULT_URL
from ..types import validate_path

log = logging.getLogger(__name__)


class ClanDataPath(BaseModel):
    directory: Path

    @validator("directory")
    def check_directory(cls: Any, v: Path) -> Path:  # noqa
        return validate_path(clan_data_dir(), v)


class ClanFlakePath(BaseModel):
    flake_name: Path

    @validator("flake_name")
    def check_flake_name(cls: Any, v: Path) -> Path:  # noqa
        return validate_path(clan_flakes_dir(), v)


class FlakeCreateInput(ClanFlakePath):
    url: AnyUrl = DEFAULT_URL
