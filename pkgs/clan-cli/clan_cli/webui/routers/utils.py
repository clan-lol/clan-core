import asyncio
import logging
import shlex

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)


class NixBuildException(HTTPException):
    def __init__(self, msg: str, loc: list = ["body", "flake_attr"]):
        detail = [
            {
                "loc": loc,
                "msg": msg,
                "type": "value_error",
            }
        ]
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


def nix_build_exception_handler(
    request: Request, exc: NixBuildException
) -> JSONResponse:
    log.error("NixBuildException: %s", exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(dict(detail=exc.detail)),
    )


async def run_cmd(cmd: list[str]) -> bytes:
    log.debug(f"Running command: {shlex.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise NixBuildException(
            f"""
command: {shlex.join(cmd)}
exit code: {proc.returncode}
command output:
{stderr.decode("utf-8")}
"""
        )
    return stdout
