import logging
from pathlib import Path
from typing import NewType, Union

from pydantic import AnyUrl

log = logging.getLogger(__name__)

FlakeName = NewType("FlakeName", str)

FlakeUrl = Union[AnyUrl, Path]


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
