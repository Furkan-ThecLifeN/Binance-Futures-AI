from __future__ import annotations

import asyncio

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.analytics.service import (
    load_market_snapshot,
    normalize_symbol,
)


router = APIRouter()


@router.websocket(
    "/ws/market/{symbol}"
)
async def market_websocket(
    websocket: WebSocket,
    symbol: str,
):
    symbol = normalize_symbol(
        symbol
    )

    await websocket.accept()

    try:
        while True:
            snapshot = (
                await load_market_snapshot(
                    symbol
                )
            )

            await websocket.send_json(
                {
                    "type":
                        "market_update",

                    "symbol":
                        symbol,

                    "data":
                        snapshot,
                }
            )

            await asyncio.sleep(
                1.0
            )

    except WebSocketDisconnect:
        return

    except asyncio.CancelledError:
        raise

    except Exception:
        try:
            await websocket.close(
                code=1011
            )
        except Exception:
            pass