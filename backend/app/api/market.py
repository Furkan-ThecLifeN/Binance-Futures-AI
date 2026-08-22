from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.analytics.service import (
    load_candle_rows,
    load_derivatives_analysis,
    load_market_snapshot,
    load_orderbook_analysis,
    normalize_symbol,
)


router = APIRouter(
    tags=[
        "market",
    ]
)


@router.get(
    "/market/{symbol}"
)
async def get_market(
    symbol: str,
):
    symbol = normalize_symbol(
        symbol
    )

    result = await load_market_snapshot(
        symbol
    )

    if (
        result["price"]
        is None
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                f"No live market "
                f"state for {symbol}"
            ),
        )

    return result


@router.get(
    "/market/{symbol}/candles"
)
async def get_candles(
    symbol: str,

    interval: str = Query(
        default="5m",
    ),

    limit: int = Query(
        default=300,
        ge=1,
        le=1000,
    ),
):
    try:
        candles = await load_candle_rows(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "symbol":
            normalize_symbol(
                symbol
            ),

        "interval":
            interval,

        "count":
            len(candles),

        "candles":
            candles,
    }


@router.get(
    "/market/{symbol}/orderbook"
)
async def get_orderbook(
    symbol: str,
):
    return await load_orderbook_analysis(
        symbol
    )


@router.get(
    "/market/{symbol}/derivatives"
)
async def get_derivatives(
    symbol: str,
):
    try:
        return await load_derivatives_analysis(
            symbol
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to load "
                "Binance derivatives data"
            ),
        ) from exc