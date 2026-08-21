from __future__ import annotations

import asyncio
import json
import logging
import random
from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any

import websockets
from websockets.exceptions import (
    ConnectionClosed,
)

from app.binance.schemas import (
    AggTradeEvent,
    BookTickerEvent,
    DepthEvent,
    DepthLevel,
    KlineEvent,
    StreamMessage,
)

from app.binance.subscriptions import (
    build_combined_stream_url,
    build_market_streams,
    build_public_streams,
)

from app.config import settings


logger = logging.getLogger(
    __name__
)


MessageHandler = Callable[
    [StreamMessage],
    Awaitable[None],
]


class BinanceWebSocketManager:
    def __init__(
        self,
        symbol: str = "BTCUSDT",
        message_handler: (
            MessageHandler | None
        ) = None,
    ) -> None:

        self.symbol = (
            symbol.upper()
        )

        self.message_handler = (
            message_handler
        )

        # -------------------------
        # MARKET STREAM
        # -------------------------

        self.market_streams = (
            build_market_streams(
                self.symbol
            )
        )

        self.market_url = (
            build_combined_stream_url(
                settings
                .binance_market_ws_base_url,
                self.market_streams,
            )
        )

        # -------------------------
        # PUBLIC STREAM
        # -------------------------

        self.public_streams = (
            build_public_streams(
                self.symbol
            )
        )

        self.public_url = (
            build_combined_stream_url(
                settings
                .binance_public_ws_base_url,
                self.public_streams,
            )
        )

        self._running = False

        self.max_backoff_seconds = (
            30.0
        )

        self._market_reconnect_attempt = 0

        self._public_reconnect_attempt = 0


    async def start(
        self,
    ) -> None:

        self._running = True

        logger.info(
            "Starting Binance "
            "WebSocket manager for %s",
            self.symbol,
        )

        market_task = (
            asyncio.create_task(
                self._connection_loop(
                    name="market",
                    url=self.market_url,
                )
            )
        )

        public_task = (
            asyncio.create_task(
                self._connection_loop(
                    name="public",
                    url=self.public_url,
                )
            )
        )

        try:
            await asyncio.gather(
                market_task,
                public_task,
            )

        except asyncio.CancelledError:

            market_task.cancel()
            public_task.cancel()

            await asyncio.gather(
                market_task,
                public_task,
                return_exceptions=True,
            )

            raise


    async def stop(
        self,
    ) -> None:

        self._running = False


    async def _connection_loop(
        self,
        name: str,
        url: str,
    ) -> None:

        while self._running:

            try:
                await self._connect(
                    name=name,
                    url=url,
                )

            except asyncio.CancelledError:
                raise

            except Exception as exc:
                logger.exception(
                    "Binance %s WebSocket "
                    "error: %s",
                    name,
                    exc,
                )

            if not self._running:
                break

            delay = (
                self._calculate_backoff(
                    name
                )
            )

            logger.warning(
                "Binance %s reconnect "
                "in %.2f seconds",
                name,
                delay,
            )

            await asyncio.sleep(
                delay
            )


    def _calculate_backoff(
        self,
        connection_name: str,
    ) -> float:

        if connection_name == "market":

            self._market_reconnect_attempt += 1

            attempt = (
                self
                ._market_reconnect_attempt
            )

        else:

            self._public_reconnect_attempt += 1

            attempt = (
                self
                ._public_reconnect_attempt
            )

        exponential = min(
            2 ** (
                attempt - 1
            ),
            self.max_backoff_seconds,
        )

        jitter = random.uniform(
            0.0,
            1.0,
        )

        return min(
            exponential + jitter,
            self.max_backoff_seconds,
        )


    def _reset_backoff(
        self,
        connection_name: str,
    ) -> None:

        if (
            connection_name
            == "market"
        ):
            self._market_reconnect_attempt = 0

        else:
            self._public_reconnect_attempt = 0


    async def _connect(
        self,
        name: str,
        url: str,
    ) -> None:

        logger.info(
            "Connecting Binance "
            "%s WS: %s",
            name,
            url,
        )

        async with websockets.connect(
            url,

            ping_interval=20,
            ping_timeout=20,

            close_timeout=10,

            max_queue=4096,
        ) as websocket:

            self._reset_backoff(
                name
            )

            logger.info(
                "Binance %s "
                "WebSocket connected",
                name,
            )

            message_count = 0

            try:

                async for raw_message in websocket:

                    if not self._running:
                        break

                    message_count += 1

                    try:

                        if (
                            message_count
                            <= 3
                        ):
                            logger.info(
                                "Binance %s raw "
                                "message received #%s",
                                name,
                                message_count,
                            )

                        parsed = (
                            self._parse_message(
                                raw_message
                            )
                        )

                        if parsed is None:
                            continue

                        if (
                            message_count
                            <= 10
                        ):
                            logger.info(
                                "Binance %s "
                                "parsed event: "
                                "%s stream=%s",
                                name,
                                parsed.event_type,
                                parsed.stream,
                            )

                        if (
                            self.message_handler
                            is not None
                        ):
                            await (
                                self
                                .message_handler(
                                    parsed
                                )
                            )

                    except Exception:
                        logger.exception(
                            "Failed to "
                            "process Binance "
                            "%s message",
                            name,
                        )

            except ConnectionClosed as exc:

                logger.warning(
                    "Binance %s "
                    "WebSocket connection "
                    "closed: %s",
                    name,
                    exc,
                )


    def _parse_message(
        self,
        raw_message: (
            str | bytes
        ),
    ) -> StreamMessage | None:

        if isinstance(
            raw_message,
            bytes,
        ):
            raw_message = (
                raw_message.decode(
                    "utf-8"
                )
            )

        payload: dict[
            str,
            Any,
        ] = json.loads(
            raw_message
        )

        stream = str(
            payload.get(
                "stream",
                "",
            )
        )

        data = payload.get(
            "data",
            payload,
        )

        if not isinstance(
            data,
            dict,
        ):
            logger.warning(
                "Unexpected Binance "
                "payload: %s",
                payload,
            )

            return None

        event_type = (
            data.get("e")
        )

        if event_type == "kline":

            event = (
                self._parse_kline(
                    data
                )
            )

        elif event_type == "aggTrade":

            event = (
                self._parse_agg_trade(
                    data
                )
            )

        elif event_type == "bookTicker":

            event = (
                self._parse_book_ticker(
                    data
                )
            )

        elif event_type == "depthUpdate":

            event = (
                self._parse_depth(
                    data
                )
            )

        else:

            logger.debug(
                "Ignored Binance "
                "event type: %s",
                event_type,
            )

            return None

        return StreamMessage(
            stream=stream,
            event_type=str(
                event_type
            ),
            symbol=data.get("s"),
            data=event,
        )


    @staticmethod
    def _parse_kline(
        data: dict[
            str,
            Any,
        ],
    ) -> KlineEvent:

        kline = data["k"]

        return KlineEvent(
            event_type=data["e"],

            event_time=int(
                data["E"]
            ),

            symbol=data["s"],

            interval=kline["i"],

            open_time=int(
                kline["t"]
            ),

            close_time=int(
                kline["T"]
            ),

            open=float(
                kline["o"]
            ),

            high=float(
                kline["h"]
            ),

            low=float(
                kline["l"]
            ),

            close=float(
                kline["c"]
            ),

            volume=float(
                kline["v"]
            ),

            quote_volume=float(
                kline["q"]
            ),

            trades=int(
                kline["n"]
            ),

            taker_buy_base_volume=float(
                kline["V"]
            ),

            taker_buy_quote_volume=float(
                kline["Q"]
            ),

            closed=bool(
                kline["x"]
            ),
        )


    @staticmethod
    def _parse_agg_trade(
        data: dict[
            str,
            Any,
        ],
    ) -> AggTradeEvent:

        return AggTradeEvent(
            event_type=data["e"],

            event_time=int(
                data["E"]
            ),

            symbol=data["s"],

            aggregate_trade_id=int(
                data["a"]
            ),

            price=float(
                data["p"]
            ),

            quantity=float(
                data["q"]
            ),

            first_trade_id=int(
                data["f"]
            ),

            last_trade_id=int(
                data["l"]
            ),

            trade_time=int(
                data["T"]
            ),

            buyer_is_market_maker=bool(
                data["m"]
            ),
        )


    @staticmethod
    def _parse_book_ticker(
        data: dict[
            str,
            Any,
        ],
    ) -> BookTickerEvent:

        return BookTickerEvent(
            event_type=data.get(
                "e",
                "bookTicker",
            ),

            event_time=int(
                data.get(
                    "E",
                    data.get(
                        "T",
                        0,
                    ),
                )
            ),

            symbol=data["s"],

            update_id=int(
                data["u"]
            ),

            best_bid_price=float(
                data["b"]
            ),

            best_bid_quantity=float(
                data["B"]
            ),

            best_ask_price=float(
                data["a"]
            ),

            best_ask_quantity=float(
                data["A"]
            ),
        )


    @staticmethod
    def _parse_depth(
        data: dict[
            str,
            Any,
        ],
    ) -> DepthEvent:

        bids = [
            DepthLevel(
                price=float(
                    level[0]
                ),

                quantity=float(
                    level[1]
                ),
            )

            for level
            in data.get(
                "b",
                [],
            )

            if len(level) >= 2
        ]

        asks = [
            DepthLevel(
                price=float(
                    level[0]
                ),

                quantity=float(
                    level[1]
                ),
            )

            for level
            in data.get(
                "a",
                [],
            )

            if len(level) >= 2
        ]

        return DepthEvent(
            event_type=data["e"],

            event_time=int(
                data["E"]
            ),

            transaction_time=int(
                data.get(
                    "T",
                    data["E"],
                )
            ),

            symbol=data["s"],

            first_update_id=int(
                data["U"]
            ),

            final_update_id=int(
                data["u"]
            ),

            previous_final_update_id=int(
                data.get(
                    "pu",
                    0,
                )
            ),

            bids=bids,
            asks=asks,
        )