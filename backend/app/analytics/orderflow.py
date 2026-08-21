from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pandas as pd


def analyze_orderflow(
    trades: pd.DataFrame,
    large_trade_quantile: float = 0.95,
) -> dict:
    if trades.empty:
        return {
            "buy_volume": 0.0,
            "sell_volume": 0.0,
            "delta": 0.0,
            "cvd": 0.0,
            "buy_ratio": 0.0,
            "sell_ratio": 0.0,
            "trade_velocity_1m": 0,
            "large_trade_count": 0,
        }

    required = {
        "quantity",
        "buyer_is_market_maker",
    }

    missing = (
        required
        - set(trades.columns)
    )

    if missing:
        raise ValueError(
            f"Missing trade columns: "
            f"{sorted(missing)}"
        )

    result = trades.copy()

    result["quantity"] = (
        result["quantity"]
        .astype(float)
    )

    result["buy_volume"] = (
        result["quantity"].where(
            ~result[
                "buyer_is_market_maker"
            ].astype(bool),
            0.0,
        )
    )

    result["sell_volume"] = (
        result["quantity"].where(
            result[
                "buyer_is_market_maker"
            ].astype(bool),
            0.0,
        )
    )

    result["delta"] = (
        result["buy_volume"]
        - result["sell_volume"]
    )

    result["cvd"] = (
        result["delta"].cumsum()
    )

    buy_volume = float(
        result[
            "buy_volume"
        ].sum()
    )

    sell_volume = float(
        result[
            "sell_volume"
        ].sum()
    )

    total_volume = (
        buy_volume
        + sell_volume
    )

    if (
        "event_time"
        in result.columns
    ):
        timestamps = pd.to_datetime(
            result["event_time"],
            utc=True,
        )

        cutoff = (
            datetime.now(
                timezone.utc
            )
            - timedelta(
                minutes=1
            )
        )

        trade_velocity = int(
            (
                timestamps
                >= cutoff
            ).sum()
        )

    else:
        trade_velocity = int(
            len(result)
        )

    threshold = float(
        result["quantity"]
        .quantile(
            large_trade_quantile
        )
    )

    large_trade_count = int(
        (
            result["quantity"]
            >= threshold
        ).sum()
    )

    return {
        "buy_volume":
            buy_volume,

        "sell_volume":
            sell_volume,

        "delta":
            buy_volume
            - sell_volume,

        "cvd":
            float(
                result[
                    "cvd"
                ].iloc[-1]
            ),

        "buy_ratio":
            (
                buy_volume
                / total_volume
                if total_volume
                else 0.0
            ),

        "sell_ratio":
            (
                sell_volume
                / total_volume
                if total_volume
                else 0.0
            ),

        "trade_velocity_1m":
            trade_velocity,

        "large_trade_threshold":
            threshold,

        "large_trade_count":
            large_trade_count,
    }