from __future__ import annotations

import pandas as pd


def detect_swings(
    frame: pd.DataFrame,
    left: int = 2,
    right: int = 2,
) -> pd.DataFrame:
    result = frame.copy()

    result[
        "swing_high"
    ] = False

    result[
        "swing_low"
    ] = False

    if len(result) < (
        left + right + 1
    ):
        return result

    highs = (
        result["high"]
        .astype(float)
    )

    lows = (
        result["low"]
        .astype(float)
    )

    for position in range(
        left,
        len(result) - right,
    ):
        high_window = highs.iloc[
            position - left:
            position + right + 1
        ]

        low_window = lows.iloc[
            position - left:
            position + right + 1
        ]

        current_high = (
            highs.iloc[position]
        )

        current_low = (
            lows.iloc[position]
        )

        if (
            current_high
            == high_window.max()
            and (
                high_window
                == current_high
            ).sum()
            == 1
        ):
            result.iloc[
                position,
                result.columns.get_loc(
                    "swing_high"
                ),
            ] = True

        if (
            current_low
            == low_window.min()
            and (
                low_window
                == current_low
            ).sum()
            == 1
        ):
            result.iloc[
                position,
                result.columns.get_loc(
                    "swing_low"
                ),
            ] = True

    return result


def classify_structure(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    result = detect_swings(
        frame
    )

    result[
        "structure_label"
    ] = None

    previous_high: float | None = None
    previous_low: float | None = None

    for index in result.index:
        if bool(
            result.at[
                index,
                "swing_high",
            ]
        ):
            current = float(
                result.at[
                    index,
                    "high",
                ]
            )

            if previous_high is not None:
                result.at[
                    index,
                    "structure_label",
                ] = (
                    "HH"
                    if current
                    > previous_high
                    else "LH"
                )

            previous_high = current

        if bool(
            result.at[
                index,
                "swing_low",
            ]
        ):
            current = float(
                result.at[
                    index,
                    "low",
                ]
            )

            if previous_low is not None:
                result.at[
                    index,
                    "structure_label",
                ] = (
                    "HL"
                    if current
                    > previous_low
                    else "LL"
                )

            previous_low = current

    return result


def analyze_structure(
    frame: pd.DataFrame,
) -> dict:
    result = classify_structure(
        frame
    )

    swing_highs = result[
        result["swing_high"]
    ]

    swing_lows = result[
        result["swing_low"]
    ]

    last_high = (
        float(
            swing_highs.iloc[-1][
                "high"
            ]
        )
        if not swing_highs.empty
        else None
    )

    last_low = (
        float(
            swing_lows.iloc[-1][
                "low"
            ]
        )
        if not swing_lows.empty
        else None
    )

    labels = (
        result[
            "structure_label"
        ]
        .dropna()
        .tolist()
    )

    recent_labels = labels[-4:]

    trend = "RANGE"

    if (
        "HH" in recent_labels
        and "HL" in recent_labels
    ):
        trend = "BULLISH"

    elif (
        "LH" in recent_labels
        and "LL" in recent_labels
    ):
        trend = "BEARISH"

    current_close = float(
        result.iloc[-1][
            "close"
        ]
    )

    event = None

    if (
        last_high is not None
        and current_close
        > last_high
    ):
        if trend == "BEARISH":
            event = "CHOCH_BULLISH"
        else:
            event = "BOS_BULLISH"

    elif (
        last_low is not None
        and current_close
        < last_low
    ):
        if trend == "BULLISH":
            event = "CHOCH_BEARISH"
        else:
            event = "BOS_BEARISH"

    return {
        "trend": trend,
        "event": event,
        "last_swing_high":
            last_high,
        "last_swing_low":
            last_low,
        "recent_labels":
            recent_labels,
    }