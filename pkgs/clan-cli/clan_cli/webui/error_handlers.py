import logging

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..errors import ClanError
from .settings import settings

log = logging.getLogger(__name__)


def clan_error_handler(request: Request, exc: Exception) -> JSONResponse:
    headers = {}

    if settings.env.is_development():
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "*"

    if isinstance(exc, ClanError):
        log.error(f"ClanError: {exc}")
        detail = [
            {
                "loc": [],
                "msg": str(exc),
            }
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(dict(detail=detail)),
            headers=headers,
        )
    else:
        log.exception(f"Unhandled Exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                dict(
                    detail=[
                        {
                            "loc": [],
                            "msg": str(exc),
                        }
                    ]
                )
            ),
            headers=headers,
        )
