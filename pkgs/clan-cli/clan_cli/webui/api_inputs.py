import logging
from pathlib import Path
from typing import Any

from pydantic import AnyUrl, BaseModel, validator

from ..dirs import clan_data_dir, clan_flakes_dir
from ..flakes.create import DEFAULT_URL
from ..types import validate_path


log = logging.getLogger(__name__)

class ClanDataPath(BaseModel):
    dest: Path

    @validator("dest")
    def check_data_path(cls: Any, v: Path) -> Path:  # noqa
        return validate_path(clan_data_dir(), v)


class ClanFlakePath(BaseModel):
    dest: Path

    @validator("dest")
    def check_dest(cls: Any, v: Path) -> Path:  # noqa
        return validate_path(clan_flakes_dir(), v)


class FlakeCreateInput(ClanFlakePath):
    url: AnyUrl = DEFAULT_URL
