import logging

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..errors import ClanError

log = logging.getLogger(__name__)


def clan_error_handler(request: Request, exc: ClanError) -> JSONResponse:
    log.error("ClanError: %s", exc)
    detail = [
        {
            "loc": [],
            "msg": str(exc),
        }
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(dict(detail=detail)),
    )
