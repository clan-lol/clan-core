import logging
import os
from mimetypes import guess_type
from pathlib import Path

from fastapi import APIRouter, Response

from ..assets import asset_path
from ..tags import Tags

router = APIRouter()

log = logging.getLogger(__name__)


@router.get("/{path_name:path}", tags=[Tags.root])
async def root(path_name: str) -> Response:
    if path_name == "":
        path_name = "index.html"
    filename = Path(os.path.normpath(asset_path() / path_name))

    if not filename.is_relative_to(asset_path()):
        log.error("Prevented directory traversal: %s", filename)
        # prevent directory traversal
        return Response(status_code=403)

    if not filename.is_file():
        if filename.suffix == "":
            filename = filename.with_suffix(".html")
            if not filename.is_file():
                log.error("File not found: %s", filename)
                return Response(status_code=404)

    content_type, _ = guess_type(filename)
    return Response(filename.read_bytes(), media_type=content_type)
