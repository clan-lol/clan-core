from pathlib import Path
from typing import Union

loc: Path = Path(__file__).parent


def get_asset(name: Union[str, Path]) -> Path:
    return loc / name
