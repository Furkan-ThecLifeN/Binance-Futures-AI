from __future__ import annotations


REGIMES = {
    "TRENDING_BULLISH",
    "TRENDING_BEARISH",
    "RANGING",
    "BREAKOUT",
    "VOL_EXPANSION",
    "COMPRESSION",
    "CHAOTIC",
}


def classify_regime(
    *,
    close: float,

    ema_20: float | None,
    ema_50: float | None,
    ema_200: float | None,

    rsi_14: float | None,

    structure_trend: str,

    structure_event: str | None,

    rvol: float | None,

    volatility_state: str,
) -> dict:

    bullish_alignment = (
        ema_20 is not None
        and ema_50 is not None
        and close > ema_20
        > ema_50
    )

    bearish_alignment = (
        ema_20 is not None
        and ema_50 is not None
        and close < ema_20
        < ema_50
    )

    if (
        structure_event
        in {
            "BOS_BULLISH",
            "BOS_BEARISH",
        }
        and rvol is not None
        and rvol >= 1.5
    ):
        regime = "BREAKOUT"

    elif (
        volatility_state
        == "COMPRESSION"
    ):
        regime = "COMPRESSION"

    elif (
        volatility_state
        == "EXPANSION"
        and structure_trend
        == "RANGE"
    ):
        regime = "VOL_EXPANSION"

    elif (
        bullish_alignment
        and structure_trend
        == "BULLISH"
        and (
            rsi_14 is None
            or rsi_14 >= 50
        )
    ):
        regime = (
            "TRENDING_BULLISH"
        )

    elif (
        bearish_alignment
        and structure_trend
        == "BEARISH"
        and (
            rsi_14 is None
            or rsi_14 <= 50
        )
    ):
        regime = (
            "TRENDING_BEARISH"
        )

    elif (
        structure_trend
        == "RANGE"
        and (
            rvol is None
            or rvol < 1.3
        )
    ):
        regime = "RANGING"

    else:
        regime = "CHAOTIC"

    above_ema_200 = (
        ema_200 is not None
        and close > ema_200
    )

    below_ema_200 = (
        ema_200 is not None
        and close < ema_200
    )

    return {
        "regime":
            regime,

        "bullish_alignment":
            bullish_alignment,

        "bearish_alignment":
            bearish_alignment,

        "above_ema_200":
            above_ema_200,

        "below_ema_200":
            below_ema_200,
    }