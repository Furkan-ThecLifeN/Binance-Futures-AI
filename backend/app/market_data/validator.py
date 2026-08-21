from __future__ import annotations

from collections import deque
from datetime import datetime, timezone

from pydantic import BaseModel

from app.market_data.normalizer import (
    NormalizedEvent,
)


INTERVAL_MILLISECONDS = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "1h": 3_600_000,
}


class ValidationResult(BaseModel):
    accepted: bool = True

    duplicate: bool = False
    stale: bool = False

    missing_candles: int = 0

    orderbook_synced: bool = True

    warnings: list[str] = []
    errors: list[str] = []


class MarketDataValidator:
    def __init__(
        self,
        stale_threshold_seconds: int = 10,
        duplicate_cache_size: int = 20_000,
    ) -> None:

        self.stale_threshold_seconds = (
            stale_threshold_seconds
        )

        self.duplicate_cache_size = (
            duplicate_cache_size
        )

        self._seen: set[str] = set()
        self._seen_order: deque[str] = deque()

        self._last_closed_candle: dict[
            tuple[str, str],
            int,
        ] = {}

        self._depth_last_update_id: dict[
            str,
            int,
        ] = {}

        self._orderbook_synced: dict[
            str,
            bool,
        ] = {}


    def set_order_book_snapshot(
        self,
        symbol: str,
        last_update_id: int,
    ) -> None:

        symbol = symbol.upper()

        self._depth_last_update_id[
            symbol
        ] = last_update_id

        self._orderbook_synced[
            symbol
        ] = False


    def reset_order_book(
        self,
        symbol: str,
    ) -> None:

        symbol = symbol.upper()

        self._depth_last_update_id.pop(
            symbol,
            None,
        )

        self._orderbook_synced[
            symbol
        ] = False


    def is_orderbook_synced(
        self,
        symbol: str,
    ) -> bool:

        return self._orderbook_synced.get(
            symbol.upper(),
            False,
        )


    def get_depth_last_update_id(
        self,
        symbol: str,
    ) -> int | None:

        return self._depth_last_update_id.get(
            symbol.upper()
        )


    def validate(
        self,
        event: NormalizedEvent,
    ) -> ValidationResult:

        result = ValidationResult()

        self._validate_stale(
            event,
            result,
        )

        self._validate_duplicate(
            event,
            result,
        )

        if event.event_type == "kline":
            self._validate_candle(
                event,
                result,
            )

        if event.event_type == "depthUpdate":
            self._validate_depth(
                event,
                result,
            )

        if result.stale:
            result.accepted = False

        if result.duplicate:
            result.accepted = False

        if result.errors:
            result.accepted = False

        return result


    def _validate_stale(
        self,
        event: NormalizedEvent,
        result: ValidationResult,
    ) -> None:

        now = datetime.now(
            timezone.utc
        )

        age_seconds = (
            now - event.event_time
        ).total_seconds()

        if (
            age_seconds
            > self.stale_threshold_seconds
        ):
            result.stale = True

            result.errors.append(
                f"stale_data:"
                f"{age_seconds:.2f}s"
            )


    def _build_duplicate_key(
        self,
        event: NormalizedEvent,
    ) -> str | None:

        # aggTrade ID gerçekten event kimliği
        # olarak kullanılabilir.
        if event.event_type == "aggTrade":
            return (
                f"aggTrade:"
                f"{event.symbol}:"
                f"{event.sequence_id}"
            )

        # bookTicker update_id değerleri bazı
        # mesajlarda tekrar görülebilir.
        # Bu nedenle duplicate filtresine
        # sokmuyoruz.
        if event.event_type == "bookTicker":
            return None

        # Depth sequence kontrolü zaten
        # _validate_depth içinde yapılıyor.
        # Burada tekrar duplicate kontrolü
        # yapmak yanlış pozitif üretebilir.
        if event.event_type == "depthUpdate":
            return None

        if (
            event.event_type == "kline"
            and event.data.get("closed")
        ):
            open_time = event.data[
                "open_time"
            ]

            interval = event.data[
                "interval"
            ]

            return (
                f"kline:"
                f"{event.symbol}:"
                f"{interval}:"
                f"{open_time}"
            )

        return None


    def _validate_duplicate(
        self,
        event: NormalizedEvent,
        result: ValidationResult,
    ) -> None:

        key = self._build_duplicate_key(
            event
        )

        if key is None:
            return

        if key in self._seen:
            result.duplicate = True

            result.warnings.append(
                "duplicate_event"
            )

            return

        self._seen.add(key)
        self._seen_order.append(key)

        while (
            len(self._seen_order)
            > self.duplicate_cache_size
        ):
            old_key = (
                self._seen_order.popleft()
            )

            self._seen.discard(
                old_key
            )


    def _validate_candle(
        self,
        event: NormalizedEvent,
        result: ValidationResult,
    ) -> None:

        if not event.data.get(
            "closed"
        ):
            return

        interval = str(
            event.data["interval"]
        )

        expected_ms = (
            INTERVAL_MILLISECONDS.get(
                interval
            )
        )

        if expected_ms is None:
            return

        open_time = event.data[
            "open_time"
        ]

        current_ms = int(
            open_time.timestamp()
            * 1000
        )

        key = (
            event.symbol,
            interval,
        )

        previous_ms = (
            self._last_closed_candle.get(
                key
            )
        )

        if previous_ms is not None:
            difference = (
                current_ms
                - previous_ms
            )

            if difference > expected_ms:
                missing = (
                    difference
                    // expected_ms
                    - 1
                )

                result.missing_candles = int(
                    missing
                )

                result.warnings.append(
                    f"missing_candles:"
                    f"{missing}"
                )

        self._last_closed_candle[
            key
        ] = current_ms


    def _validate_depth(
        self,
        event: NormalizedEvent,
        result: ValidationResult,
    ) -> None:

        symbol = event.symbol.upper()

        first_id = int(
            event.data[
                "first_update_id"
            ]
        )

        final_id = int(
            event.data[
                "final_update_id"
            ]
        )

        previous_final_id = int(
            event.data.get(
                "previous_final_update_id",
                0,
            )
        )

        last_id = (
            self._depth_last_update_id.get(
                symbol
            )
        )

        if last_id is None:
            self._orderbook_synced[
                symbol
            ] = False

            result.orderbook_synced = False

            result.errors.append(
                "orderbook_snapshot_missing"
            )

            return

        # Snapshot veya mevcut local state
        # bu event'i zaten içeriyor.
        if final_id <= last_id:
            result.accepted = False

            result.orderbook_synced = (
                self.is_orderbook_synced(
                    symbol
                )
            )

            result.warnings.append(
                "old_depth_event"
            )

            return

        currently_synced = (
            self._orderbook_synced.get(
                symbol,
                False,
            )
        )

        # İlk geçerli event snapshot'ın
        # hemen sonrasını kapsamalı.
        if not currently_synced:

            target_id = last_id + 1

            if (
                first_id
                <= target_id
                <= final_id
            ):
                self._depth_last_update_id[
                    symbol
                ] = final_id

                self._orderbook_synced[
                    symbol
                ] = True

                result.orderbook_synced = True

                return

            result.orderbook_synced = False

            result.accepted = False

            result.warnings.append(
                "waiting_for_snapshot_overlap"
            )

            return

        # Senkron olduktan sonra Futures
        # depth stream'deki pu, önceki
        # event'in u değerine eşit olmalı.
        if (
            previous_final_id > 0
            and previous_final_id
            != last_id
        ):
            self._orderbook_synced[
                symbol
            ] = False

            result.orderbook_synced = False

            result.errors.append(
                "orderbook_sequence_gap"
            )

            return

        self._depth_last_update_id[
            symbol
        ] = final_id

        result.orderbook_synced = True