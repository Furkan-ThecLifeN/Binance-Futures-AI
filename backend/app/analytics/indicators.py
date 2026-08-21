from __future__ import annotations

import numpy as np
import pandas as pd


EMA_PERIODS = (
    9,
    20,
    50,
    100,
    200,
)

RSI_PERIODS = (
    7,
    14,
)


def _require_columns(
    frame: pd.DataFrame,
    columns: tuple[str, ...],
) -> None:
    missing = [
        column
        for column in columns
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )


def calculate_ema(
    series: pd.Series,
    period: int,
) -> pd.Series:
    return series.ewm(
        span=period,
        adjust=False,
        min_periods=period,
    ).mean()


def calculate_rsi(
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    delta = close.diff()

    gain = delta.clip(
        lower=0.0
    )

    loss = -delta.clip(
        upper=0.0
    )

    average_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    rs = (
        average_gain
        / average_loss.replace(
            0.0,
            np.nan,
        )
    )

    rsi = (
        100.0
        - (
            100.0
            / (
                1.0 + rs
            )
        )
    )

    # Sadece kazanç varsa RSI 100.
    rsi = rsi.mask(
        (average_loss == 0)
        & (average_gain > 0),
        100.0,
    )

    # Hareket yoksa nötr kabul et.
    rsi = rsi.mask(
        (average_loss == 0)
        & (average_gain == 0),
        50.0,
    )

    return rsi


def calculate_true_range(
    frame: pd.DataFrame,
) -> pd.Series:
    previous_close = (
        frame["close"].shift(1)
    )

    high_low = (
        frame["high"]
        - frame["low"]
    ).abs()

    high_previous = (
        frame["high"]
        - previous_close
    ).abs()

    low_previous = (
        frame["low"]
        - previous_close
    ).abs()

    values = pd.concat(
        [
            high_low,
            high_previous,
            low_previous,
        ],
        axis=1,
    )

    return values.max(
        axis=1
    )


def calculate_atr(
    frame: pd.DataFrame,
    period: int = 14,
) -> pd.Series:
    true_range = (
        calculate_true_range(
            frame
        )
    )

    return true_range.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()


def calculate_vwap(
    frame: pd.DataFrame,
) -> pd.Series:
    typical_price = (
        frame["high"]
        + frame["low"]
        + frame["close"]
    ) / 3.0

    volume = (
        frame["volume"]
        .astype(float)
    )

    cumulative_volume = (
        volume.cumsum()
    )

    cumulative_value = (
        (
            typical_price
            * volume
        ).cumsum()
    )

    return (
        cumulative_value
        / cumulative_volume.replace(
            0.0,
            np.nan,
        )
    )


def calculate_indicators(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        frame,
        (
            "high",
            "low",
            "close",
            "volume",
        ),
    )

    result = (
        frame.copy()
        .sort_index()
    )

    close = (
        result["close"]
        .astype(float)
    )

    for period in EMA_PERIODS:
        result[
            f"ema_{period}"
        ] = calculate_ema(
            close,
            period,
        )

    for period in RSI_PERIODS:
        result[
            f"rsi_{period}"
        ] = calculate_rsi(
            close,
            period,
        )

    result["atr_14"] = (
        calculate_atr(
            result,
            14,
        )
    )

    result["atr_pct"] = (
        result["atr_14"]
        / result["close"]
        * 100.0
    )

    result["vwap"] = (
        calculate_vwap(
            result
        )
    )

    return result


def latest_indicator_snapshot(
    frame: pd.DataFrame,
) -> dict:
    calculated = (
        calculate_indicators(
            frame
        )
    )

    if calculated.empty:
        return {}

    last = calculated.iloc[-1]

    fields = [
        "close",
        "ema_9",
        "ema_20",
        "ema_50",
        "ema_100",
        "ema_200",
        "rsi_7",
        "rsi_14",
        "atr_14",
        "atr_pct",
        "vwap",
    ]

    result: dict[str, float | None] = {}

    for field in fields:
        value = last.get(field)

        result[field] = (
            None
            if pd.isna(value)
            else float(value)
        )

    return result