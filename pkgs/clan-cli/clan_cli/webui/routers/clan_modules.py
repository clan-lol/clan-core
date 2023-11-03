# Logging setup
import logging

from fastapi import APIRouter, HTTPException

from clan_cli.clan_modules import get_clan_module_names
from clan_cli.types import FlakeName

from ..api_outputs import (
    ClanModulesResponse,
)
from ..tags import Tags

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/{flake_name}/clan_modules", tags=[Tags.modules])
async def list_clan_modules(flake_name: FlakeName) -> ClanModulesResponse:
    module_names, error = get_clan_module_names(flake_name)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    return ClanModulesResponse(clan_modules=module_names)
