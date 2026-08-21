from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from app.config import settings


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)


async def initialize_database() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                CREATE EXTENSION IF NOT EXISTS timescaledb
                """
            )
        )

        await connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS candles (
                    symbol TEXT NOT NULL,
                    interval TEXT NOT NULL,

                    open_time TIMESTAMPTZ NOT NULL,
                    close_time TIMESTAMPTZ NOT NULL,

                    open DOUBLE PRECISION NOT NULL,
                    high DOUBLE PRECISION NOT NULL,
                    low DOUBLE PRECISION NOT NULL,
                    close DOUBLE PRECISION NOT NULL,

                    volume DOUBLE PRECISION NOT NULL,
                    quote_volume DOUBLE PRECISION NOT NULL,

                    trades INTEGER NOT NULL,

                    taker_buy_base_volume
                        DOUBLE PRECISION NOT NULL,

                    taker_buy_quote_volume
                        DOUBLE PRECISION NOT NULL,

                    PRIMARY KEY (
                        symbol,
                        interval,
                        open_time
                    )
                )
                """
            )
        )

        await connection.execute(
            text(
                """
                SELECT create_hypertable(
                    'candles',
                    by_range('open_time'),
                    if_not_exists => TRUE
                )
                """
            )
        )

        await connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_candles_symbol_interval_time
                ON candles (
                    symbol,
                    interval,
                    open_time DESC
                )
                """
            )
        )

        await connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS market_metrics (
                    symbol TEXT NOT NULL,
                    metric_type TEXT NOT NULL,

                    event_time TIMESTAMPTZ NOT NULL,

                    sequence_id BIGINT NOT NULL,

                    payload JSONB NOT NULL,

                    PRIMARY KEY (
                        symbol,
                        metric_type,
                        event_time,
                        sequence_id
                    )
                )
                """
            )
        )

        await connection.execute(
            text(
                """
                SELECT create_hypertable(
                    'market_metrics',
                    by_range('event_time'),
                    if_not_exists => TRUE
                )
                """
            )
        )

        await connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_market_metrics_symbol_time
                ON market_metrics (
                    symbol,
                    event_time DESC
                )
                """
            )
        )


async def close_database() -> None:
    await engine.dispose()