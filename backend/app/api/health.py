from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def get_health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }