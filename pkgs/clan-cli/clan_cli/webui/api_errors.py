import logging

from pydantic import BaseModel

log = logging.getLogger(__name__)


class MissingClanImports(BaseModel):
    missing_clan_imports: list[str] = []
    msg: str = "Some requested clan modules could not be found"
