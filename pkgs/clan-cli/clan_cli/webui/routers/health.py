from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> str:
    return "OK"
