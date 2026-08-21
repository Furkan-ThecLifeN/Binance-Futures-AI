from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


async def check_database() -> bool:
    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False

    finally:
        await engine.dispose()


async def check_redis() -> bool:
    redis_client = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    try:
        result = await redis_client.ping()

        return bool(result)

    except Exception:
        return False

    finally:
        await redis_client.aclose()


@router.get("")
async def get_health():
    database_ok = await check_database()
    redis_ok = await check_redis()

    all_healthy = database_ok and redis_ok

    response = {
        "status": "ok" if all_healthy else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {
            "database": "ok" if database_ok else "error",
            "redis": "ok" if redis_ok else "error",
        },
    }

    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content=response,
    )