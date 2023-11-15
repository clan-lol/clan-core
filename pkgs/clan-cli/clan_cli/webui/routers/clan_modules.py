# Logging setup
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from clan_cli.clan_modules import get_clan_module_names

from ..api_outputs import (
    ClanModulesResponse,
)
from ..tags import Tags

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/clan_modules", tags=[Tags.modules])
async def list_clan_modules(flake_dir: Path) -> ClanModulesResponse:
    module_names, error = get_clan_module_names(flake_dir)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    return ClanModulesResponse(clan_modules=module_names)
