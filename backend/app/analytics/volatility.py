from __future__ import annotations

import numpy as np
import pandas as pd

from app.analytics.indicators import (
    calculate_atr,
)


def calculate_realized_volatility(
    close: pd.Series,
    window: int = 20,
) -> pd.Series:
    log_returns = np.log(
        close
        / close.shift(1)
    )

    return (
        log_returns
        .rolling(
            window,
            min_periods=window,
        )
        .std()
        * np.sqrt(window)
        * 100.0
    )


def calculate_volatility(
    frame: pd.DataFrame,
    window: int = 20,
) -> pd.DataFrame:

    result = frame.copy()

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

    result[
        "realized_volatility"
    ] = (
        calculate_realized_volatility(
            result[
                "close"
            ].astype(float),
            window,
        )
    )

    result["range_pct"] = (
        (
            result["high"]
            - result["low"]
        )
        / result["close"]
        * 100.0
    )

    result[
        "atr_pct_baseline"
    ] = (
        result["atr_pct"]
        .rolling(
            50,
            min_periods=20,
        )
        .median()
    )

    return result


def latest_volatility_snapshot(
    frame: pd.DataFrame,
) -> dict:

    result = (
        calculate_volatility(
            frame
        )
    )

    if result.empty:
        return {}

    last = result.iloc[-1]

    atr_pct = last.get(
        "atr_pct"
    )

    baseline = last.get(
        "atr_pct_baseline"
    )

    state = "NORMAL"

    if (
        not pd.isna(atr_pct)
        and not pd.isna(baseline)
        and baseline > 0
    ):
        ratio = (
            atr_pct
            / baseline
        )

        if ratio >= 1.35:
            state = "EXPANSION"

        elif ratio <= 0.75:
            state = "COMPRESSION"

    return {
        "atr":
            (
                None
                if pd.isna(
                    last["atr_14"]
                )
                else float(
                    last["atr_14"]
                )
            ),

        "atr_pct":
            (
                None
                if pd.isna(
                    atr_pct
                )
                else float(
                    atr_pct
                )
            ),

        "realized_volatility":
            (
                None
                if pd.isna(
                    last[
                        "realized_volatility"
                    ]
                )
                else float(
                    last[
                        "realized_volatility"
                    ]
                )
            ),

        "range_pct":
            float(
                last[
                    "range_pct"
                ]
            ),

        "state":
            state,
    }