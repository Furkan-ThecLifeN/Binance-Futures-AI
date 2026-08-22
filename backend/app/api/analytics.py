from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.analytics.service import (
    build_analytics_snapshot,
)


router = APIRouter(
    tags=[
        "analytics",
    ]
)


@router.get(
    "/analytics/{symbol}"
)
async def get_analytics(
    symbol: str,

    interval: str = Query(
        default="5m",
    ),
):
    try:
        return await (
            build_analytics_snapshot(
                symbol=symbol,
                interval=interval,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Analytics calculation "
                "failed"
            ),
        ) from exc