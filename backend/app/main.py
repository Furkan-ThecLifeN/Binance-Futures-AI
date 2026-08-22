import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import (
    router as analytics_router,
)
from app.api.health import (
    router as health_router,
)
from app.api.market import (
    router as market_router,
)
from app.api.websocket import (
    router as websocket_router,
)

from app.binance.schemas import (
    StreamMessage,
)
from app.binance.websocket_manager import (
    BinanceWebSocketManager,
)
from app.config import settings
from app.market_data.collector import (
    MarketDataCollector,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    __name__
)


collector = MarketDataCollector()


async def handle_binance_message(
    message: StreamMessage,
) -> None:
    await collector.handle_message(
        message
    )


binance_ws = BinanceWebSocketManager(
    symbol=(
        settings
        .binance_default_symbol
    ),
    message_handler=(
        handle_binance_message
    ),
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    await collector.initialize()

    websocket_task = (
        asyncio.create_task(
            binance_ws.start()
        )
    )

    logger.info(
        "Binance data layer started for %s",
        settings.binance_default_symbol,
    )

    try:
        yield

    finally:
        await binance_ws.stop()

        websocket_task.cancel()

        try:
            await websocket_task
        except asyncio.CancelledError:
            pass

        logger.info(
            "Binance data layer stopped"
        )


app = FastAPI(
    title="Binance Futures AI Market Intelligence",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api",
)

app.include_router(
    market_router,
    prefix="/api",
)

app.include_router(
    analytics_router,
    prefix="/api",
)

app.include_router(
    websocket_router,
)