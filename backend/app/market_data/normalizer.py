from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

from app.binance.schemas import (
    AggTradeEvent,
    BookTickerEvent,
    DepthEvent,
    KlineEvent,
    StreamMessage,
)


class NormalizedEvent(BaseModel):
    event_type: str
    symbol: str

    event_time: datetime
    received_at: datetime

    sequence_id: int | None = None

    data: dict[str, Any]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def milliseconds_to_utc(
    timestamp_ms: int,
) -> datetime:

    return datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=timezone.utc,
    )


def normalize_stream_message(
    message: StreamMessage,
) -> NormalizedEvent:

    received_at = utc_now()

    if message.event_type == "kline":
        event: KlineEvent = message.data

        return NormalizedEvent(
            event_type="kline",
            symbol=event.symbol.upper(),

            event_time=milliseconds_to_utc(
                event.event_time
            ),

            received_at=received_at,

            sequence_id=event.open_time,

            data={
                "interval": event.interval,

                "open_time": milliseconds_to_utc(
                    event.open_time
                ),

                "close_time": milliseconds_to_utc(
                    event.close_time
                ),

                "open": event.open,
                "high": event.high,
                "low": event.low,
                "close": event.close,

                "volume": event.volume,
                "quote_volume": event.quote_volume,

                "trades": event.trades,

                "taker_buy_base_volume":
                    event.taker_buy_base_volume,

                "taker_buy_quote_volume":
                    event.taker_buy_quote_volume,

                "closed": event.closed,
            },
        )

    if message.event_type == "aggTrade":
        event: AggTradeEvent = message.data

        return NormalizedEvent(
            event_type="aggTrade",
            symbol=event.symbol.upper(),

            event_time=milliseconds_to_utc(
                event.event_time
            ),

            received_at=received_at,

            sequence_id=event.aggregate_trade_id,

            data={
                "aggregate_trade_id":
                    event.aggregate_trade_id,

                "price": event.price,
                "quantity": event.quantity,

                "first_trade_id":
                    event.first_trade_id,

                "last_trade_id":
                    event.last_trade_id,

                "trade_time":
                    milliseconds_to_utc(
                        event.trade_time
                    ),

                "buyer_is_market_maker":
                    event.buyer_is_market_maker,
            },
        )

    if message.event_type == "bookTicker":
        event: BookTickerEvent = message.data

        return NormalizedEvent(
            event_type="bookTicker",
            symbol=event.symbol.upper(),

            event_time=milliseconds_to_utc(
                event.event_time
            ),

            received_at=received_at,

            sequence_id=event.update_id,

            data={
                "update_id":
                    event.update_id,

                "best_bid_price":
                    event.best_bid_price,

                "best_bid_quantity":
                    event.best_bid_quantity,

                "best_ask_price":
                    event.best_ask_price,

                "best_ask_quantity":
                    event.best_ask_quantity,
            },
        )

    if message.event_type == "depthUpdate":
        event: DepthEvent = message.data

        return NormalizedEvent(
            event_type="depthUpdate",
            symbol=event.symbol.upper(),

            event_time=milliseconds_to_utc(
                event.event_time
            ),

            received_at=received_at,

            sequence_id=event.final_update_id,

            data={
                "transaction_time":
                    milliseconds_to_utc(
                        event.transaction_time
                    ),

                "first_update_id":
                    event.first_update_id,

                "final_update_id":
                    event.final_update_id,

                "previous_final_update_id":
                    event.previous_final_update_id,

                "bids": [
                    [
                        level.price,
                        level.quantity,
                    ]
                    for level in event.bids
                ],

                "asks": [
                    [
                        level.price,
                        level.quantity,
                    ]
                    for level in event.asks
                ],
            },
        )

    raise ValueError(
        f"Unsupported event type: "
        f"{message.event_type}"
    )