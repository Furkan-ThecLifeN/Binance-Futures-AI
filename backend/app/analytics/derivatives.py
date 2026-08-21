from __future__ import annotations

import pandas as pd


def calculate_change_pct(
    current: float,
    previous: float | None,
) -> float | None:
    if (
        previous is None
        or previous == 0
    ):
        return None

    return (
        (
            current
            - previous
        )
        / abs(previous)
        * 100.0
    )


def classify_price_oi(
    price_change_pct:
        float | None,

    oi_change_pct:
        float | None,
) -> str:

    if (
        price_change_pct is None
        or oi_change_pct is None
    ):
        return "UNKNOWN"

    if (
        price_change_pct > 0
        and oi_change_pct > 0
    ):
        return (
            "PRICE_UP_OI_UP"
        )

    if (
        price_change_pct > 0
        and oi_change_pct < 0
    ):
        return (
            "PRICE_UP_OI_DOWN"
        )

    if (
        price_change_pct < 0
        and oi_change_pct > 0
    ):
        return (
            "PRICE_DOWN_OI_UP"
        )

    if (
        price_change_pct < 0
        and oi_change_pct < 0
    ):
        return (
            "PRICE_DOWN_OI_DOWN"
        )

    return "NEUTRAL"


def analyze_derivatives(
    current_price: float,
    previous_price: float | None,

    current_oi: float,
    previous_oi: float | None,

    funding_rate: float | None,
) -> dict:

    price_change_pct = (
        calculate_change_pct(
            current_price,
            previous_price,
        )
    )

    oi_change_pct = (
        calculate_change_pct(
            current_oi,
            previous_oi,
        )
    )

    funding_bias = (
        "NEUTRAL"
    )

    if funding_rate is not None:
        if funding_rate > 0:
            funding_bias = (
                "LONGS_PAY_SHORTS"
            )

        elif funding_rate < 0:
            funding_bias = (
                "SHORTS_PAY_LONGS"
            )

    return {
        "open_interest":
            current_oi,

        "oi_change_pct":
            oi_change_pct,

        "funding_rate":
            funding_rate,

        "funding_bias":
            funding_bias,

        "price_change_pct":
            price_change_pct,

        "price_oi_relation":
            classify_price_oi(
                price_change_pct,
                oi_change_pct,
            ),
    }


def oi_change_over_period(
    oi_series: pd.Series,
    periods: int,
) -> float | None:
    if len(oi_series) <= periods:
        return None

    current = float(
        oi_series.iloc[-1]
    )

    previous = float(
        oi_series.iloc[
            -periods - 1
        ]
    )

    return calculate_change_pct(
        current,
        previous,
    )