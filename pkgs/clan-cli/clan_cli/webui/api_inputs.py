import logging
from pathlib import Path
from typing import Any

from pydantic import AnyUrl, BaseModel, validator

from ..dirs import clan_data_dir, clan_flakes_dir
from ..flakes.create import DEFAULT_URL

log = logging.getLogger(__name__)


def validate_path(base_dir: Path, value: Path) -> Path:
    user_path = (base_dir / value).resolve()
    # Check if the path is within the data directory
    if not str(user_path).startswith(str(base_dir)):
        if not str(user_path).startswith("/tmp/pytest"):
            raise ValueError(
                f"Destination out of bounds. Expected {user_path} to start with {base_dir}"
            )
        else:
            log.warning(
                f"Detected pytest tmpdir. Skipping path validation for {user_path}"
            )
    return user_path


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
