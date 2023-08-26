import functools
from pathlib import Path


@functools.cache
def asset_path() -> Path:
    return Path(__file__).parent / "assets"
