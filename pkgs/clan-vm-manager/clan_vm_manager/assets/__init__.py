from pathlib import Path
from typing import Union

loc: Path = Path(__file__).parent


def get_asset(name: str | Path) -> Path:
    return loc / name
