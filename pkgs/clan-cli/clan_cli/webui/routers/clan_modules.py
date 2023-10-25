# Logging setup
import logging

from fastapi import APIRouter, HTTPException

from clan_cli.clan_modules import get_clan_module_names

from ..schemas import (
    ClanModulesResponse,
)

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/clan_modules")
async def list_clan_modules() -> ClanModulesResponse:
    module_names, error = get_clan_module_names()
    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    return ClanModulesResponse(clan_modules=module_names)
