from __future__ import annotations

import json
from typing import Any

import pandas as pd
from sqlalchemy import text

from app.analytics.confluence import (
    calculate_confluence,
)
from app.analytics.derivatives import (
    analyze_derivatives,
)
from app.analytics.indicators import (
    latest_indicator_snapshot,
)
from app.analytics.levels import (
    calculate_levels,
)
from app.analytics.orderbook import (
    analyze_orderbook,
)
from app.analytics.orderflow import (
    analyze_orderflow,
)
from app.analytics.regime import (
    classify_regime,
)
from app.analytics.structure import (
    analyze_structure,
)
from app.analytics.volatility import (
    latest_volatility_snapshot,
)
from app.analytics.volume import (
    latest_volume_snapshot,
)
from app.binance.rest_client import (
    binance_rest_client,
)
from app.cache.redis_client import (
    redis_client,
)
from app.database.session import (
    engine,
)


ALLOWED_INTERVALS = {
    "1m",
    "5m",
    "15m",
    "1h",
}


def normalize_symbol(
    symbol: str,
) -> str:
    return (
        symbol
        .strip()
        .upper()
    )


def validate_interval(
    interval: str,
) -> str:
    interval = (
        interval
        .strip()
        .lower()
    )

    if interval not in ALLOWED_INTERVALS:
        raise ValueError(
            "Unsupported interval. "
            "Allowed: 1m, 5m, 15m, 1h"
        )

    return interval


async def load_candle_rows(
    symbol: str,
    interval: str = "5m",
    limit: int = 300,
) -> list[dict[str, Any]]:

    symbol = normalize_symbol(
        symbol
    )

    interval = validate_interval(
        interval
    )

    limit = max(
        1,
        min(
            int(limit),
            1000,
        ),
    )

    async with engine.connect() as connection:
        result = await connection.execute(
            text(
                """
                SELECT
                    symbol,
                    interval,
                    open_time,
                    close_time,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    quote_volume,
                    trades,
                    taker_buy_base_volume,
                    taker_buy_quote_volume
                FROM candles
                WHERE
                    symbol = :symbol
                    AND interval = :interval
                ORDER BY open_time DESC
                LIMIT :limit
                """
            ),
            {
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
            },
        )

        rows = (
            result
            .mappings()
            .all()
        )

    rows = list(
        reversed(rows)
    )

    return [
        {
            "symbol":
                row["symbol"],

            "interval":
                row["interval"],

            "open_time":
                row["open_time"]
                .isoformat(),

            "close_time":
                row["close_time"]
                .isoformat(),

            "open":
                float(row["open"]),

            "high":
                float(row["high"]),

            "low":
                float(row["low"]),

            "close":
                float(row["close"]),

            "volume":
                float(row["volume"]),

            "quote_volume":
                float(
                    row["quote_volume"]
                ),

            "trades":
                int(row["trades"]),

            "taker_buy_base_volume":
                float(
                    row[
                        "taker_buy_base_volume"
                    ]
                ),

            "taker_buy_quote_volume":
                float(
                    row[
                        "taker_buy_quote_volume"
                    ]
                ),
        }
        for row in rows
    ]


async def load_candle_frame(
    symbol: str,
    interval: str = "5m",
    limit: int = 300,
) -> pd.DataFrame:

    rows = await load_candle_rows(
        symbol=symbol,
        interval=interval,
        limit=limit,
    )

    if not rows:
        return pd.DataFrame()

    frame = pd.DataFrame(
        rows
    )

    frame["open_time"] = (
        pd.to_datetime(
            frame["open_time"],
            utc=True,
        )
    )

    frame = frame.set_index(
        "open_time"
    )

    return frame


async def _load_json_redis(
    key: str,
) -> dict[str, Any] | None:

    raw = await redis_client.get(
        key
    )

    if raw is None:
        return None

    try:
        value = json.loads(
            raw
        )

    except json.JSONDecodeError:
        return None

    if not isinstance(
        value,
        dict,
    ):
        return None

    return value


async def load_market_snapshot(
    symbol: str,
) -> dict[str, Any]:

    symbol = normalize_symbol(
        symbol
    )

    price_raw = await redis_client.get(
        f"market:{symbol}:price"
    )

    price = (
        float(price_raw)
        if price_raw is not None
        else None
    )

    health = await _load_json_redis(
        f"market:{symbol}:health"
    )

    trade = await _load_json_redis(
        f"market:{symbol}:trade"
    )

    book_ticker = await _load_json_redis(
        f"market:{symbol}:book_ticker"
    )

    kline_1m = await _load_json_redis(
        f"market:{symbol}:kline:1m"
    )

    kline_5m = await _load_json_redis(
        f"market:{symbol}:kline:5m"
    )

    kline_15m = await _load_json_redis(
        f"market:{symbol}:kline:15m"
    )

    kline_1h = await _load_json_redis(
        f"market:{symbol}:kline:1h"
    )

    return {
        "symbol":
            symbol,

        "price":
            price,

        "health":
            health,

        "trade":
            trade,

        "book_ticker":
            book_ticker,

        "klines": {
            "1m":
                kline_1m,

            "5m":
                kline_5m,

            "15m":
                kline_15m,

            "1h":
                kline_1h,
        },
    }


async def load_orderbook_analysis(
    symbol: str,
) -> dict[str, Any]:

    symbol = normalize_symbol(
        symbol
    )

    raw = await _load_json_redis(
        f"market:{symbol}:book"
    )

    if not raw:
        return analyze_orderbook(
            bids=[],
            asks=[],
        )

    bids = raw.get(
        "bids",
        [],
    )

    asks = raw.get(
        "asks",
        [],
    )

    result = analyze_orderbook(
        bids=bids,
        asks=asks,
    )

    result["synced"] = bool(
        raw.get(
            "synced",
            False,
        )
    )

    result["last_update_id"] = (
        raw.get(
            "last_update_id"
        )
    )

    result["snapshot_time"] = (
        raw.get(
            "snapshot_time"
        )
    )

    return result


async def load_orderflow_analysis(
    symbol: str,
    limit: int = 500,
) -> dict[str, Any]:

    symbol = normalize_symbol(
        symbol
    )

    async with engine.connect() as connection:
        result = await connection.execute(
            text(
                """
                SELECT
                    event_time,
                    payload
                FROM market_metrics
                WHERE
                    symbol = :symbol
                    AND metric_type = 'aggTrade'
                ORDER BY event_time DESC
                LIMIT :limit
                """
            ),
            {
                "symbol":
                    symbol,

                "limit":
                    max(
                        1,
                        min(
                            int(limit),
                            2000,
                        ),
                    ),
            },
        )

        rows = (
            result
            .mappings()
            .all()
        )

    trades: list[
        dict[str, Any]
    ] = []

    for row in reversed(
        rows
    ):
        payload = row[
            "payload"
        ]

        if isinstance(
            payload,
            str,
        ):
            try:
                payload = json.loads(
                    payload
                )
            except json.JSONDecodeError:
                continue

        if not isinstance(
            payload,
            dict,
        ):
            continue

        if (
            "quantity"
            not in payload
            or
            "buyer_is_market_maker"
            not in payload
        ):
            continue

        trades.append(
            {
                "event_time":
                    row["event_time"],

                "quantity":
                    float(
                        payload[
                            "quantity"
                        ]
                    ),

                "buyer_is_market_maker":
                    bool(
                        payload[
                            "buyer_is_market_maker"
                        ]
                    ),
            }
        )

    if not trades:
        return analyze_orderflow(
            pd.DataFrame()
        )

    frame = pd.DataFrame(
        trades
    )

    return analyze_orderflow(
        frame
    )


async def load_derivatives_analysis(
    symbol: str,
    current_price: float | None = None,
    previous_price: float | None = None,
) -> dict[str, Any]:

    symbol = normalize_symbol(
        symbol
    )

    oi = (
        await binance_rest_client
        .get_open_interest(
            symbol
        )
    )

    funding_history = (
        await binance_rest_client
        .get_funding_history(
            symbol=symbol,
            limit=2,
        )
    )

    funding_rate = (
        funding_history[-1]
        .funding_rate

        if funding_history

        else None
    )

    funding_time = (
        funding_history[-1]
        .funding_time

        if funding_history

        else None
    )

    if current_price is None:
        price_raw = await redis_client.get(
            f"market:{symbol}:price"
        )

        current_price = (
            float(price_raw)
            if price_raw
            else 0.0
        )

    result = analyze_derivatives(
        current_price=float(
            current_price
        ),

        previous_price=(
            float(previous_price)
            if previous_price
            is not None
            else None
        ),

        current_oi=float(
            oi.open_interest
        ),

        # V1'de gerçek persistent OI
        # history henüz tutulmadığı için
        # sentetik previous OI üretmiyoruz.
        previous_oi=None,

        funding_rate=(
            funding_rate
        ),
    )

    result[
        "funding_time"
    ] = funding_time

    return result


async def build_analytics_snapshot(
    symbol: str,
    interval: str = "5m",
) -> dict[str, Any]:

    symbol = normalize_symbol(
        symbol
    )

    interval = validate_interval(
        interval
    )

    frame = await load_candle_frame(
        symbol=symbol,
        interval=interval,
        limit=300,
    )

    if frame.empty:
        raise ValueError(
            f"No candle data for "
            f"{symbol} {interval}"
        )

    if len(frame) < 2:
        raise ValueError(
            "At least 2 candles "
            "are required"
        )

    indicators = (
        latest_indicator_snapshot(
            frame
        )
    )

    structure = (
        analyze_structure(
            frame
        )
    )

    volume = (
        latest_volume_snapshot(
            frame
        )
    )

    volatility = (
        latest_volatility_snapshot(
            frame
        )
    )

    levels = calculate_levels(
        frame,
        atr=indicators.get(
            "atr_14"
        ),
    )

    regime = classify_regime(
        close=float(
            frame.iloc[-1][
                "close"
            ]
        ),

        ema_20=indicators.get(
            "ema_20"
        ),

        ema_50=indicators.get(
            "ema_50"
        ),

        ema_200=indicators.get(
            "ema_200"
        ),

        rsi_14=indicators.get(
            "rsi_14"
        ),

        structure_trend=(
            structure["trend"]
        ),

        structure_event=(
            structure["event"]
        ),

        rvol=volume.get(
            "rvol"
        ),

        volatility_state=(
            volatility[
                "state"
            ]
        ),
    )

    orderflow = (
        await load_orderflow_analysis(
            symbol
        )
    )

    orderbook = (
        await load_orderbook_analysis(
            symbol
        )
    )

    current_price = float(
        frame.iloc[-1][
            "close"
        ]
    )

    previous_price = float(
        frame.iloc[-2][
            "close"
        ]
    )

    derivatives = (
        await load_derivatives_analysis(
            symbol=symbol,
            current_price=current_price,
            previous_price=previous_price,
        )
    )

    confluence = calculate_confluence(
        indicators=indicators,
        structure=structure,
        volume=volume,
        orderflow=orderflow,
        orderbook=orderbook,
        derivatives=derivatives,
        levels=levels,
        volatility=volatility,
        regime=regime,
    )

    return {
        "symbol":
            symbol,

        "interval":
            interval,

        "technical_indicators":
            indicators,

        "market_structure":
            structure,

        "volume_analysis":
            volume,

        "order_flow":
            orderflow,

        "order_book":
            orderbook,

        "derivatives":
            derivatives,

        "support_resistance":
            levels,

        "volatility":
            volatility,

        "market_regime":
            regime,

        "confluence":
            confluence.model_dump(),
    }