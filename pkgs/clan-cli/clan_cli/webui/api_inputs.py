import logging

from pydantic import AnyUrl, BaseModel, Extra, parse_obj_as

from ..flakes.create import DEFAULT_URL

log = logging.getLogger(__name__)


class FlakeCreateInput(BaseModel):
    url: AnyUrl = parse_obj_as(AnyUrl, DEFAULT_URL)


class MachineConfig(BaseModel):
    clanImports: list[str] = []  # noqa: N815
    clan: dict = {}

    # allow extra fields to cover the full spectrum of a nixos config
    class Config:
        extra = Extra.allow
