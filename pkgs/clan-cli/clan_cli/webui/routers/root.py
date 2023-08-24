from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/")
async def root() -> Response:
    body = "<html><body><h1>Welcome</h1></body></html>"
    return Response(content=body, media_type="text/html")
