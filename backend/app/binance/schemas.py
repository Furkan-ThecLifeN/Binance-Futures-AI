from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class Candle(BaseModel):
    open_time: int
    close_time: int

    symbol: str
    interval: str

    open: float
    high: float
    low: float
    close: float
    volume: float

    quote_volume: float = 0.0
    trades: int = 0

    taker_buy_base_volume: float = 0.0
    taker_buy_quote_volume: float = 0.0

    closed: bool = True


class OpenInterest(BaseModel):
    symbol: str
    open_interest: float
    time: int | None = None


class FundingRate(BaseModel):
    symbol: str
    funding_rate: float
    funding_time: int
    mark_price: float | None = None


class KlineEvent(BaseModel):
    event_type: str
    event_time: int

    symbol: str
    interval: str

    open_time: int
    close_time: int

    open: float
    high: float
    low: float
    close: float
    volume: float

    quote_volume: float
    trades: int

    taker_buy_base_volume: float
    taker_buy_quote_volume: float

    closed: bool


class AggTradeEvent(BaseModel):
    event_type: str
    event_time: int
    symbol: str

    aggregate_trade_id: int

    price: float
    quantity: float

    first_trade_id: int
    last_trade_id: int
    trade_time: int

    buyer_is_market_maker: bool


class BookTickerEvent(BaseModel):
    event_type: str = "bookTicker"
    event_time: int

    symbol: str

    update_id: int

    best_bid_price: float
    best_bid_quantity: float

    best_ask_price: float
    best_ask_quantity: float


class DepthLevel(BaseModel):
    price: float
    quantity: float


class DepthEvent(BaseModel):
    event_type: str
    event_time: int
    transaction_time: int

    symbol: str

    first_update_id: int
    final_update_id: int
    previous_final_update_id: int

    bids: list[DepthLevel]
    asks: list[DepthLevel]


class StreamMessage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: str
    event_type: str
    symbol: str | None = None
    data: Any