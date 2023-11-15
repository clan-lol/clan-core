import logging
from pathlib import Path
from typing import Union

from pydantic import AnyUrl

log = logging.getLogger(__name__)

FlakeUrl = Union[AnyUrl, Path]
