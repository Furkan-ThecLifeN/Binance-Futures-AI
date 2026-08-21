from __future__ import annotations

import pandas as pd

from app.analytics.structure import (
    detect_swings,
)


def _cluster_levels(
    prices: list[float],
    tolerance: float,
) -> list[dict]:
    if not prices:
        return []

    groups: list[
        list[float]
    ] = []

    for price in sorted(prices):
        matched = False

        for group in groups:
            average = (
                sum(group)
                / len(group)
            )

            if (
                abs(
                    price - average
                )
                <= tolerance
            ):
                group.append(
                    price
                )

                matched = True
                break

        if not matched:
            groups.append(
                [price]
            )

    return [
        {
            "price": (
                sum(group)
                / len(group)
            ),
            "strength": len(
                group
            ),
        }
        for group in groups
    ]


def calculate_levels(
    frame: pd.DataFrame,
    atr: float | None = None,
) -> dict:
    if frame.empty:
        return {
            "supports": [],
            "resistances": [],
        }

    swings = detect_swings(
        frame
    )

    high_prices = (
        swings.loc[
            swings["swing_high"],
            "high",
        ]
        .astype(float)
        .tolist()
    )

    low_prices = (
        swings.loc[
            swings["swing_low"],
            "low",
        ]
        .astype(float)
        .tolist()
    )

    current_price = float(
        frame.iloc[-1][
            "close"
        ]
    )

    if (
        atr is not None
        and atr > 0
    ):
        tolerance = (
            atr * 0.35
        )
    else:
        tolerance = (
            current_price
            * 0.0015
        )

    resistance_levels = (
        _cluster_levels(
            high_prices,
            tolerance,
        )
    )

    support_levels = (
        _cluster_levels(
            low_prices,
            tolerance,
        )
    )

    supports = [
        level
        for level
        in support_levels
        if level["price"]
        < current_price
    ]

    resistances = [
        level
        for level
        in resistance_levels
        if level["price"]
        > current_price
    ]

    supports.sort(
        key=lambda item:
            current_price
            - item["price"]
    )

    resistances.sort(
        key=lambda item:
            item["price"]
            - current_price
    )

    for level in supports:
        level[
            "distance_pct"
        ] = (
            (
                current_price
                - level["price"]
            )
            / current_price
            * 100.0
        )

    for level in resistances:
        level[
            "distance_pct"
        ] = (
            (
                level["price"]
                - current_price
            )
            / current_price
            * 100.0
        )

    return {
        "current_price":
            current_price,

        "supports":
            supports[:5],

        "resistances":
            resistances[:5],
    }