import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.health import (
    router as health_router,
)

from app.binance.schemas import (
    StreamMessage,
)

from app.binance.websocket_manager import (
    BinanceWebSocketManager,
)

from app.cache.redis_client import (
    close_redis,
)

from app.config import settings

from app.database.session import (
    close_database,
)

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


logger = logging.getLogger(__name__)


collector = MarketDataCollector()


async def handle_binance_message(
    message: StreamMessage,
) -> None:

    await collector.handle_message(
        message
    )


binance_ws = BinanceWebSocketManager(
    symbol=settings.binance_default_symbol,
    message_handler=handle_binance_message,
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
        "Binance data layer started "
        "for %s",
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

        await close_redis()
        await close_database()

        logger.info(
            "Binance data layer stopped"
        )


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Binance Futures AI "
        "Market Intelligence Backend API"
    ),
    lifespan=lifespan,
)


allowed_origins = [
    settings.frontend_origin,
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix=settings.api_prefix,
)