from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_rvol(
    volume: pd.Series,
    period: int = 20,
) -> pd.Series:
    baseline = (
        volume.shift(1)
        .rolling(
            period,
            min_periods=period,
        )
        .mean()
    )

    return (
        volume
        / baseline.replace(
            0.0,
            np.nan,
        )
    )


def calculate_volume_metrics(
    frame: pd.DataFrame,
    period: int = 20,
) -> pd.DataFrame:
    if "volume" not in frame.columns:
        raise ValueError(
            "volume column is required"
        )

    result = frame.copy()

    volume = (
        result["volume"]
        .astype(float)
    )

    result["volume_sma"] = (
        volume.rolling(
            period,
            min_periods=period,
        ).mean()
    )

    result["rvol"] = (
        calculate_rvol(
            volume,
            period,
        )
    )

    result[
        "volume_change_pct"
    ] = (
        volume.pct_change()
        * 100.0
    )

    short_average = (
        volume.rolling(
            5,
            min_periods=5,
        ).mean()
    )

    long_average = (
        volume.rolling(
            period,
            min_periods=period,
        ).mean()
    )

    result[
        "volume_acceleration"
    ] = (
        short_average
        / long_average.replace(
            0.0,
            np.nan,
        )
    )

    return result


def latest_volume_snapshot(
    frame: pd.DataFrame,
) -> dict:
    result = (
        calculate_volume_metrics(
            frame
        )
    )

    if result.empty:
        return {}

    last = result.iloc[-1]

    fields = (
        "volume",
        "volume_sma",
        "rvol",
        "volume_change_pct",
        "volume_acceleration",
    )

    return {
        field: (
            None
            if pd.isna(
                last.get(field)
            )
            else float(
                last[field]
            )
        )
        for field in fields
    }