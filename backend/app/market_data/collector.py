from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import deque
from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import text

from app.binance.rest_client import (
    binance_rest_client,
)

from app.binance.schemas import (
    StreamMessage,
)

from app.cache.redis_client import (
    redis_client,
)

from app.config import settings

from app.database.session import (
    engine,
    initialize_database,
)

from app.market_data.normalizer import (
    NormalizedEvent,
    milliseconds_to_utc,
    normalize_stream_message,
)

from app.market_data.validator import (
    MarketDataValidator,
    ValidationResult,
)


logger = logging.getLogger(
    __name__
)


class MarketDataCollector:
    def __init__(self) -> None:

        self.symbol = (
            settings
            .binance_default_symbol
            .upper()
        )

        self.validator = (
            MarketDataValidator()
        )

        self._last_metric_write: dict[
            tuple[str, str],
            float,
        ] = {}

        self._metric_write_interval = 1.0

        self._missing_candles = 0
        self._duplicate_events = 0
        self._stale_events = 0

        # Depth stream event'lerini
        # snapshot senkronizasyonu sırasında
        # burada tutuyoruz.
        self._depth_buffer: deque[
            NormalizedEvent
        ] = deque(
            maxlen=10_000
        )

        self._orderbook_syncing = False

        self._orderbook_sync_lock = (
            asyncio.Lock()
        )


    async def initialize(
        self,
    ) -> None:

        logger.info(
            "Initializing market data storage"
        )

        await initialize_database()

        await redis_client.ping()

        await self._backfill_candles()

        # WebSocket henüz başlamadığı için
        # burada sadece başlangıç snapshot'ı
        # alıyoruz.
        await self._load_order_book_snapshot()

        logger.info(
            "Market collector ready for %s",
            self.symbol,
        )


    async def handle_message(
        self,
        message: StreamMessage,
    ) -> None:

        try:
            event = normalize_stream_message(
                message
            )

        except Exception:
            logger.exception(
                "Market normalization failed"
            )

            return

        # Depth event'lerini mutlaka önce
        # buffer'a koyuyoruz.
        if event.event_type == "depthUpdate":
            self._depth_buffer.append(
                event
            )

        validation = (
            self.validator.validate(
                event
            )
        )

        if validation.missing_candles:
            self._missing_candles += (
                validation.missing_candles
            )

            logger.warning(
                "Missing candle detected "
                "%s %s count=%s",
                event.symbol,
                event.data.get(
                    "interval"
                ),
                validation.missing_candles,
            )

        if validation.duplicate:
            self._duplicate_events += 1

        if validation.stale:
            self._stale_events += 1

        # Depth henüz snapshot ile
        # eşleşmediyse hemen her event'te
        # snapshot istemiyoruz.
        if event.event_type == "depthUpdate":

            if (
                "orderbook_sequence_gap"
                in validation.errors
            ):
                logger.warning(
                    "Order book sequence gap "
                    "detected; scheduling resync"
                )

                self.validator.reset_order_book(
                    self.symbol
                )

                self._schedule_order_book_resync()

                await self._update_quality_state(
                    event,
                    validation,
                )

                return

            if not (
                validation.orderbook_synced
            ):
                self._schedule_order_book_resync()

                await self._update_quality_state(
                    event,
                    validation,
                )

                return

        await self._update_quality_state(
            event,
            validation,
        )

        if not validation.accepted:
            return

        await self._store_latest_state(
            event
        )

        if event.event_type == "kline":

            if event.data.get(
                "closed"
            ):
                await self._store_candle(
                    event
                )

        else:
            await self._store_metric_sample(
                event
            )


    def _schedule_order_book_resync(
        self,
    ) -> None:

        if self._orderbook_syncing:
            return

        self._orderbook_syncing = True

        asyncio.create_task(
            self._resync_order_book()
        )


    async def _resync_order_book(
        self,
    ) -> None:

        try:

            async with (
                self._orderbook_sync_lock
            ):

                logger.info(
                    "Starting order book "
                    "resynchronization"
                )

                # Kısa süre stream event'i
                # birikmesine izin veriyoruz.
                await asyncio.sleep(
                    0.25
                )

                snapshot = (
                    await binance_rest_client
                    .get_order_book_snapshot(
                        symbol=self.symbol,
                        limit=1000,
                    )
                )

                snapshot_id = int(
                    snapshot[
                        "lastUpdateId"
                    ]
                )

                self.validator.set_order_book_snapshot(
                    self.symbol,
                    snapshot_id,
                )

                # Snapshot tarafından zaten
                # kapsanmış event'leri at.
                buffered = [
                    event
                    for event
                    in list(
                        self._depth_buffer
                    )
                    if int(
                        event.data[
                            "final_update_id"
                        ]
                    )
                    > snapshot_id
                ]

                buffered.sort(
                    key=lambda event: int(
                        event.data[
                            "final_update_id"
                        ]
                    )
                )

                # Buffer'ı temizliyoruz.
                self._depth_buffer.clear()

                synced = False

                for event in buffered:

                    result = (
                        self.validator.validate(
                            event
                        )
                    )

                    if result.errors:
                        logger.warning(
                            "Buffered depth event "
                            "failed validation: %s",
                            result.errors,
                        )

                        break

                    if (
                        result.orderbook_synced
                    ):
                        synced = True

                    if result.accepted:
                        await (
                            self._store_latest_state(
                                event
                            )
                        )

                redis_payload = {
                    "symbol":
                        self.symbol,

                    "last_update_id":
                        self.validator
                        .get_depth_last_update_id(
                            self.symbol
                        )
                        or snapshot_id,

                    "bids":
                        snapshot[
                            "bids"
                        ][:50],

                    "asks":
                        snapshot[
                            "asks"
                        ][:50],

                    "synced":
                        synced,

                    "snapshot_time":
                        datetime.now(
                            timezone.utc
                        ).isoformat(),
                }

                await redis_client.set(
                    (
                        f"market:"
                        f"{self.symbol}:book"
                    ),
                    json.dumps(
                        redis_payload
                    ),
                )

                if synced:
                    logger.info(
                        "Order book synchronized "
                        "%s updateId=%s",
                        self.symbol,
                        self.validator
                        .get_depth_last_update_id(
                            self.symbol
                        ),
                    )

                else:
                    logger.info(
                        "Order book snapshot "
                        "loaded; waiting for "
                        "overlapping depth event "
                        "%s lastUpdateId=%s",
                        self.symbol,
                        snapshot_id,
                    )

        except Exception:
            logger.exception(
                "Order book "
                "resynchronization failed"
            )

        finally:
            self._orderbook_syncing = False


    async def _load_order_book_snapshot(
        self,
    ) -> None:

        snapshot = (
            await binance_rest_client
            .get_order_book_snapshot(
                symbol=self.symbol,
                limit=1000,
            )
        )

        last_update_id = int(
            snapshot[
                "lastUpdateId"
            ]
        )

        self.validator.set_order_book_snapshot(
            self.symbol,
            last_update_id,
        )

        redis_payload = {
            "symbol":
                self.symbol,

            "last_update_id":
                last_update_id,

            "bids":
                snapshot[
                    "bids"
                ][:50],

            "asks":
                snapshot[
                    "asks"
                ][:50],

            "synced":
                False,

            "snapshot_time":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

        await redis_client.set(
            (
                f"market:"
                f"{self.symbol}:book"
            ),
            json.dumps(
                redis_payload
            ),
        )

        logger.info(
            "Order book snapshot loaded "
            "%s lastUpdateId=%s",
            self.symbol,
            last_update_id,
        )


    async def _backfill_candles(
        self,
    ) -> None:

        intervals = (
            "1m",
            "5m",
            "15m",
            "1h",
        )

        now_ms = int(
            datetime.now(
                timezone.utc
            ).timestamp()
            * 1000
        )

        for interval in intervals:

            candles = (
                await binance_rest_client
                .get_klines(
                    symbol=self.symbol,
                    interval=interval,
                    limit=300,
                )
            )

            rows = []

            for candle in candles:

                if (
                    candle.close_time
                    >= now_ms
                ):
                    continue

                rows.append(
                    {
                        "symbol":
                            candle.symbol,

                        "interval":
                            candle.interval,

                        "open_time":
                            milliseconds_to_utc(
                                candle.open_time
                            ),

                        "close_time":
                            milliseconds_to_utc(
                                candle.close_time
                            ),

                        "open":
                            candle.open,

                        "high":
                            candle.high,

                        "low":
                            candle.low,

                        "close":
                            candle.close,

                        "volume":
                            candle.volume,

                        "quote_volume":
                            candle.quote_volume,

                        "trades":
                            candle.trades,

                        "taker_buy_base_volume":
                            candle
                            .taker_buy_base_volume,

                        "taker_buy_quote_volume":
                            candle
                            .taker_buy_quote_volume,
                    }
                )

            if rows:

                async with (
                    engine.begin()
                    as connection
                ):
                    await connection.execute(
                        text(
                            """
                            INSERT INTO candles (
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
                            )
                            VALUES (
                                :symbol,
                                :interval,
                                :open_time,
                                :close_time,
                                :open,
                                :high,
                                :low,
                                :close,
                                :volume,
                                :quote_volume,
                                :trades,
                                :taker_buy_base_volume,
                                :taker_buy_quote_volume
                            )
                            ON CONFLICT (
                                symbol,
                                interval,
                                open_time
                            )
                            DO UPDATE SET
                                close_time =
                                    EXCLUDED.close_time,
                                open =
                                    EXCLUDED.open,
                                high =
                                    EXCLUDED.high,
                                low =
                                    EXCLUDED.low,
                                close =
                                    EXCLUDED.close,
                                volume =
                                    EXCLUDED.volume,
                                quote_volume =
                                    EXCLUDED.quote_volume,
                                trades =
                                    EXCLUDED.trades,
                                taker_buy_base_volume =
                                    EXCLUDED
                                    .taker_buy_base_volume,
                                taker_buy_quote_volume =
                                    EXCLUDED
                                    .taker_buy_quote_volume
                            """
                        ),
                        rows,
                    )

            logger.info(
                "Backfill %s %s candles=%s",
                self.symbol,
                interval,
                len(rows),
            )


    async def _store_latest_state(
        self,
        event: NormalizedEvent,
    ) -> None:

        event_json = (
            event.model_dump(
                mode="json"
            )
        )

        payload = json.dumps(
            event_json
        )

        if event.event_type == "kline":

            interval = str(
                event.data[
                    "interval"
                ]
            )

            await redis_client.set(
                (
                    f"market:"
                    f"{event.symbol}:"
                    f"kline:{interval}"
                ),
                payload,
            )

            await redis_client.set(
                (
                    f"market:"
                    f"{event.symbol}:price"
                ),
                str(
                    event.data[
                        "close"
                    ]
                ),
            )

        elif (
            event.event_type
            == "aggTrade"
        ):

            await redis_client.set(
                (
                    f"market:"
                    f"{event.symbol}:trade"
                ),
                payload,
            )

            await redis_client.set(
                (
                    f"market:"
                    f"{event.symbol}:price"
                ),
                str(
                    event.data[
                        "price"
                    ]
                ),
            )

        elif (
            event.event_type
            == "bookTicker"
        ):

            await redis_client.set(
                (
                    f"market:"
                    f"{event.symbol}:"
                    f"book_ticker"
                ),
                payload,
            )

        elif (
            event.event_type
            == "depthUpdate"
        ):

            await redis_client.set(
                (
                    f"market:"
                    f"{event.symbol}:depth"
                ),
                payload,
            )


    async def _store_candle(
        self,
        event: NormalizedEvent,
    ) -> None:

        data = event.data

        async with (
            engine.begin()
            as connection
        ):

            await connection.execute(
                text(
                    """
                    INSERT INTO candles (
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
                    )
                    VALUES (
                        :symbol,
                        :interval,
                        :open_time,
                        :close_time,
                        :open,
                        :high,
                        :low,
                        :close,
                        :volume,
                        :quote_volume,
                        :trades,
                        :taker_buy_base_volume,
                        :taker_buy_quote_volume
                    )
                    ON CONFLICT (
                        symbol,
                        interval,
                        open_time
                    )
                    DO UPDATE SET
                        close_time =
                            EXCLUDED.close_time,
                        high =
                            EXCLUDED.high,
                        low =
                            EXCLUDED.low,
                        close =
                            EXCLUDED.close,
                        volume =
                            EXCLUDED.volume,
                        quote_volume =
                            EXCLUDED.quote_volume,
                        trades =
                            EXCLUDED.trades,
                        taker_buy_base_volume =
                            EXCLUDED
                            .taker_buy_base_volume,
                        taker_buy_quote_volume =
                            EXCLUDED
                            .taker_buy_quote_volume
                    """
                ),
                {
                    "symbol":
                        event.symbol,

                    "interval":
                        data[
                            "interval"
                        ],

                    "open_time":
                        data[
                            "open_time"
                        ],

                    "close_time":
                        data[
                            "close_time"
                        ],

                    "open":
                        data["open"],

                    "high":
                        data["high"],

                    "low":
                        data["low"],

                    "close":
                        data["close"],

                    "volume":
                        data["volume"],

                    "quote_volume":
                        data[
                            "quote_volume"
                        ],

                    "trades":
                        data["trades"],

                    "taker_buy_base_volume":
                        data[
                            "taker_buy_base_volume"
                        ],

                    "taker_buy_quote_volume":
                        data[
                            "taker_buy_quote_volume"
                        ],
                },
            )


    async def _store_metric_sample(
        self,
        event: NormalizedEvent,
    ) -> None:

        key = (
            event.symbol,
            event.event_type,
        )

        current_time = (
            time.monotonic()
        )

        previous_time = (
            self._last_metric_write.get(
                key,
                0.0,
            )
        )

        if (
            current_time
            - previous_time
            < self._metric_write_interval
        ):
            return

        self._last_metric_write[
            key
        ] = current_time

        json_data = (
            event.model_dump(
                mode="json"
            )
        )

        payload = json.dumps(
            json_data[
                "data"
            ]
        )

        sequence_id = int(
            event.sequence_id
            or 0
        )

        async with (
            engine.begin()
            as connection
        ):

            await connection.execute(
                text(
                    """
                    INSERT INTO market_metrics (
                        symbol,
                        metric_type,
                        event_time,
                        sequence_id,
                        payload
                    )
                    VALUES (
                        :symbol,
                        :metric_type,
                        :event_time,
                        :sequence_id,
                        CAST(
                            :payload
                            AS JSONB
                        )
                    )
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "symbol":
                        event.symbol,

                    "metric_type":
                        event.event_type,

                    "event_time":
                        event.event_time,

                    "sequence_id":
                        sequence_id,

                    "payload":
                        payload,
                },
            )


    async def _update_quality_state(
        self,
        event: NormalizedEvent,
        validation: ValidationResult,
    ) -> None:

        quality = {
            "symbol":
                event.symbol,

            "last_event_at":
                event.event_time.isoformat(),

            "received_at":
                event.received_at.isoformat(),

            "last_event_type":
                event.event_type,

            "stale":
                validation.stale,

            "duplicate":
                validation.duplicate,

            "missing_candles":
                self._missing_candles,

            "duplicate_events":
                self._duplicate_events,

            "stale_events":
                self._stale_events,

            "orderbook_synced":
                self.validator
                .is_orderbook_synced(
                    event.symbol
                ),

            "warnings":
                validation.warnings,

            "errors":
                validation.errors,

            "updated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

        await redis_client.set(
            (
                f"market:"
                f"{event.symbol}:health"
            ),
            json.dumps(
                quality
            ),
        )