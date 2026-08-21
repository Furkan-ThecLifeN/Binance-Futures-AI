from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


FACTOR_WEIGHTS = {
    "trend": 15.0,
    "structure": 15.0,
    "momentum": 10.0,
    "volume": 10.0,
    "orderflow": 10.0,
    "orderbook": 10.0,
    "derivatives": 10.0,
    "support_resistance": 10.0,
    "volatility": 5.0,
    "risk_reward": 5.0,
}


class FactorScore(BaseModel):
    long: float = Field(
        ge=0.0,
    )

    short: float = Field(
        ge=0.0,
    )

    max_score: float = Field(
        gt=0.0,
    )

    reasons_long: list[str] = []
    reasons_short: list[str] = []


class ConfluenceResult(BaseModel):
    long_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    short_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    setup_bias: str

    score_type: str = (
        "DETERMINISTIC_SETUP_ALIGNMENT"
    )

    probability: bool = False

    factors: dict[
        str,
        FactorScore,
    ]


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(
        minimum,
        min(
            value,
            maximum,
        ),
    )


def _score_trend(
    indicators: dict[str, Any],
    regime: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS["trend"]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    close = indicators.get(
        "close"
    )

    ema_20 = indicators.get(
        "ema_20"
    )

    ema_50 = indicators.get(
        "ema_50"
    )

    ema_200 = indicators.get(
        "ema_200"
    )

    regime_name = regime.get(
        "regime"
    )

    if (
        close is not None
        and ema_20 is not None
        and ema_50 is not None
    ):
        if (
            close > ema_20
            and ema_20 > ema_50
        ):
            long_score += 7.0

            long_reasons.append(
                "Price > EMA20 > EMA50"
            )

        elif (
            close < ema_20
            and ema_20 < ema_50
        ):
            short_score += 7.0

            short_reasons.append(
                "Price < EMA20 < EMA50"
            )

    if (
        close is not None
        and ema_200 is not None
    ):
        if close > ema_200:
            long_score += 3.0

            long_reasons.append(
                "Price above EMA200"
            )

        elif close < ema_200:
            short_score += 3.0

            short_reasons.append(
                "Price below EMA200"
            )

    if (
        regime_name
        == "TRENDING_BULLISH"
    ):
        long_score += 5.0

        long_reasons.append(
            "Bullish trending regime"
        )

    elif (
        regime_name
        == "TRENDING_BEARISH"
    ):
        short_score += 5.0

        short_reasons.append(
            "Bearish trending regime"
        )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_structure(
    structure: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "structure"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    trend = structure.get(
        "trend"
    )

    event = structure.get(
        "event"
    )

    recent_labels = (
        structure.get(
            "recent_labels"
        )
        or []
    )

    if trend == "BULLISH":
        long_score += 7.0

        long_reasons.append(
            "Bullish market structure"
        )

    elif trend == "BEARISH":
        short_score += 7.0

        short_reasons.append(
            "Bearish market structure"
        )

    if event in {
        "BOS_BULLISH",
        "CHOCH_BULLISH",
    }:
        long_score += 5.0

        long_reasons.append(
            event
        )

    elif event in {
        "BOS_BEARISH",
        "CHOCH_BEARISH",
    }:
        short_score += 5.0

        short_reasons.append(
            event
        )

    if (
        "HH" in recent_labels
        and "HL" in recent_labels
    ):
        long_score += 3.0

        long_reasons.append(
            "HH/HL sequence"
        )

    if (
        "LH" in recent_labels
        and "LL" in recent_labels
    ):
        short_score += 3.0

        short_reasons.append(
            "LH/LL sequence"
        )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_momentum(
    indicators: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "momentum"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    rsi_14 = indicators.get(
        "rsi_14"
    )

    rsi_7 = indicators.get(
        "rsi_7"
    )

    close = indicators.get(
        "close"
    )

    ema_9 = indicators.get(
        "ema_9"
    )

    ema_20 = indicators.get(
        "ema_20"
    )

    vwap = indicators.get(
        "vwap"
    )

    if rsi_14 is not None:
        if 55 <= rsi_14 <= 72:
            long_score += 4.0

            long_reasons.append(
                "RSI14 bullish momentum"
            )

        elif 28 <= rsi_14 <= 45:
            short_score += 4.0

            short_reasons.append(
                "RSI14 bearish momentum"
            )

    if rsi_7 is not None:
        if rsi_7 >= 55:
            long_score += 2.0

            long_reasons.append(
                "RSI7 bullish"
            )

        elif rsi_7 <= 45:
            short_score += 2.0

            short_reasons.append(
                "RSI7 bearish"
            )

    if (
        ema_9 is not None
        and ema_20 is not None
    ):
        if ema_9 > ema_20:
            long_score += 2.0

            long_reasons.append(
                "EMA9 above EMA20"
            )

        elif ema_9 < ema_20:
            short_score += 2.0

            short_reasons.append(
                "EMA9 below EMA20"
            )

    if (
        close is not None
        and vwap is not None
    ):
        if close > vwap:
            long_score += 2.0

            long_reasons.append(
                "Price above VWAP"
            )

        elif close < vwap:
            short_score += 2.0

            short_reasons.append(
                "Price below VWAP"
            )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_volume(
    volume: dict[str, Any],
    structure: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS["volume"]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    rvol = volume.get(
        "rvol"
    )

    acceleration = volume.get(
        "volume_acceleration"
    )

    trend = structure.get(
        "trend"
    )

    if rvol is not None:
        if rvol >= 1.5:
            base = 5.0

        elif rvol >= 1.15:
            base = 3.0

        elif rvol >= 0.9:
            base = 1.0

        else:
            base = 0.0

        if trend == "BULLISH":
            long_score += base

            if base:
                long_reasons.append(
                    "RVOL supports bullish structure"
                )

        elif trend == "BEARISH":
            short_score += base

            if base:
                short_reasons.append(
                    "RVOL supports bearish structure"
                )

        else:
            long_score += base / 2.0
            short_score += base / 2.0

    if acceleration is not None:
        if acceleration >= 1.2:
            if trend == "BULLISH":
                long_score += 5.0

                long_reasons.append(
                    "Volume accelerating"
                )

            elif trend == "BEARISH":
                short_score += 5.0

                short_reasons.append(
                    "Volume accelerating"
                )

            else:
                long_score += 2.5
                short_score += 2.5

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_orderflow(
    orderflow: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "orderflow"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    buy_ratio = (
        orderflow.get(
            "buy_ratio"
        )
    )

    sell_ratio = (
        orderflow.get(
            "sell_ratio"
        )
    )

    delta = (
        orderflow.get(
            "delta"
        )
    )

    cvd = (
        orderflow.get(
            "cvd"
        )
    )

    if buy_ratio is not None:
        if buy_ratio >= 0.65:
            long_score += 5.0

            long_reasons.append(
                "Strong aggressive buy ratio"
            )

        elif buy_ratio >= 0.55:
            long_score += 3.0

            long_reasons.append(
                "Positive aggressive buy ratio"
            )

    if sell_ratio is not None:
        if sell_ratio >= 0.65:
            short_score += 5.0

            short_reasons.append(
                "Strong aggressive sell ratio"
            )

        elif sell_ratio >= 0.55:
            short_score += 3.0

            short_reasons.append(
                "Positive aggressive sell ratio"
            )

    if delta is not None:
        if delta > 0:
            long_score += 3.0

            long_reasons.append(
                "Positive delta"
            )

        elif delta < 0:
            short_score += 3.0

            short_reasons.append(
                "Negative delta"
            )

    if cvd is not None:
        if cvd > 0:
            long_score += 2.0

            long_reasons.append(
                "Positive CVD"
            )

        elif cvd < 0:
            short_score += 2.0

            short_reasons.append(
                "Negative CVD"
            )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_orderbook(
    orderbook: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "orderbook"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    if not orderbook.get(
        "valid",
        False,
    ):
        return FactorScore(
            long=0.0,
            short=0.0,
            max_score=maximum,
        )

    imbalance = (
        orderbook.get(
            "imbalance"
        )
    )

    pressure = (
        orderbook.get(
            "pressure"
        )
    )

    spread_bps = (
        orderbook.get(
            "spread_bps"
        )
    )

    microprice = (
        orderbook.get(
            "microprice"
        )
    )

    mid_price = (
        orderbook.get(
            "mid_price"
        )
    )

    if imbalance is not None:
        if imbalance >= 0.30:
            long_score += 5.0

            long_reasons.append(
                "Strong bid imbalance"
            )

        elif imbalance >= 0.15:
            long_score += 3.0

            long_reasons.append(
                "Bid imbalance"
            )

        elif imbalance <= -0.30:
            short_score += 5.0

            short_reasons.append(
                "Strong ask imbalance"
            )

        elif imbalance <= -0.15:
            short_score += 3.0

            short_reasons.append(
                "Ask imbalance"
            )

    if pressure == "BID_PRESSURE":
        long_score += 2.0

        long_reasons.append(
            "Bid-side pressure"
        )

    elif pressure == "ASK_PRESSURE":
        short_score += 2.0

        short_reasons.append(
            "Ask-side pressure"
        )

    if (
        microprice is not None
        and mid_price is not None
    ):
        if microprice > mid_price:
            long_score += 2.0

            long_reasons.append(
                "Microprice above mid"
            )

        elif microprice < mid_price:
            short_score += 2.0

            short_reasons.append(
                "Microprice below mid"
            )

    if (
        spread_bps is not None
        and spread_bps <= 1.0
    ):
        long_score += 1.0
        short_score += 1.0

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_derivatives(
    derivatives: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "derivatives"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    relation = (
        derivatives.get(
            "price_oi_relation"
        )
    )

    oi_change = (
        derivatives.get(
            "oi_change_pct"
        )
    )

    funding_rate = (
        derivatives.get(
            "funding_rate"
        )
    )

    if relation == "PRICE_UP_OI_UP":
        long_score += 6.0

        long_reasons.append(
            "Price up + OI up"
        )

    elif (
        relation
        == "PRICE_DOWN_OI_UP"
    ):
        short_score += 6.0

        short_reasons.append(
            "Price down + OI up"
        )

    elif (
        relation
        == "PRICE_UP_OI_DOWN"
    ):
        long_score += 2.0

        long_reasons.append(
            "Price up + OI down"
        )

    elif (
        relation
        == "PRICE_DOWN_OI_DOWN"
    ):
        short_score += 2.0

        short_reasons.append(
            "Price down + OI down"
        )

    if oi_change is not None:
        if oi_change >= 1.0:
            if relation in {
                "PRICE_UP_OI_UP",
            }:
                long_score += 2.0

            elif relation in {
                "PRICE_DOWN_OI_UP",
            }:
                short_score += 2.0

    if funding_rate is not None:
        absolute_funding = abs(
            float(
                funding_rate
            )
        )

        if absolute_funding < 0.0005:
            long_score += 1.0
            short_score += 1.0

        elif funding_rate >= 0.001:
            short_score += 2.0

            short_reasons.append(
                "Elevated positive funding"
            )

        elif funding_rate <= -0.001:
            long_score += 2.0

            long_reasons.append(
                "Elevated negative funding"
            )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_support_resistance(
    levels: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "support_resistance"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    supports = (
        levels.get(
            "supports"
        )
        or []
    )

    resistances = (
        levels.get(
            "resistances"
        )
        or []
    )

    nearest_support = (
        supports[0]
        if supports
        else None
    )

    nearest_resistance = (
        resistances[0]
        if resistances
        else None
    )

    if nearest_support:
        distance = float(
            nearest_support.get(
                "distance_pct",
                999.0,
            )
        )

        strength = int(
            nearest_support.get(
                "strength",
                1,
            )
        )

        if distance <= 0.25:
            long_score += 4.0

            long_reasons.append(
                "Price near support"
            )

        elif distance <= 0.6:
            long_score += 2.0

        if strength >= 3:
            long_score += 2.0

            long_reasons.append(
                "Strong nearby support"
            )

    if nearest_resistance:
        distance = float(
            nearest_resistance.get(
                "distance_pct",
                999.0,
            )
        )

        strength = int(
            nearest_resistance.get(
                "strength",
                1,
            )
        )

        if distance <= 0.25:
            short_score += 4.0

            short_reasons.append(
                "Price near resistance"
            )

        elif distance <= 0.6:
            short_score += 2.0

        if strength >= 3:
            short_score += 2.0

            short_reasons.append(
                "Strong nearby resistance"
            )

    # Karşı yöndeki seviyenin yeterince
    # uzakta olması setup için ek alan sağlar.
    if nearest_resistance:
        resistance_distance = float(
            nearest_resistance.get(
                "distance_pct",
                0.0,
            )
        )

        if resistance_distance >= 0.75:
            long_score += 4.0

            long_reasons.append(
                "Room to resistance"
            )

    if nearest_support:
        support_distance = float(
            nearest_support.get(
                "distance_pct",
                0.0,
            )
        )

        if support_distance >= 0.75:
            short_score += 4.0

            short_reasons.append(
                "Room to support"
            )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_volatility(
    volatility: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "volatility"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    state = volatility.get(
        "state"
    )

    atr_pct = volatility.get(
        "atr_pct"
    )

    if state == "NORMAL":
        long_score += 4.0
        short_score += 4.0

    elif state == "EXPANSION":
        long_score += 3.0
        short_score += 3.0

    elif state == "COMPRESSION":
        long_score += 1.0
        short_score += 1.0

    if atr_pct is not None:
        if (
            0.10
            <= atr_pct
            <= 1.50
        ):
            long_score += 1.0
            short_score += 1.0

        elif atr_pct > 3.0:
            long_score = max(
                0.0,
                long_score - 2.0,
            )

            short_score = max(
                0.0,
                short_score - 2.0,
            )

            long_reasons.append(
                "Excessive volatility penalty"
            )

            short_reasons.append(
                "Excessive volatility penalty"
            )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def _score_risk_reward(
    levels: dict[str, Any],
) -> FactorScore:
    maximum = (
        FACTOR_WEIGHTS[
            "risk_reward"
        ]
    )

    long_score = 0.0
    short_score = 0.0

    long_reasons: list[str] = []
    short_reasons: list[str] = []

    current_price = levels.get(
        "current_price"
    )

    supports = (
        levels.get(
            "supports"
        )
        or []
    )

    resistances = (
        levels.get(
            "resistances"
        )
        or []
    )

    if (
        current_price is None
        or not supports
        or not resistances
    ):
        return FactorScore(
            long=0.0,
            short=0.0,
            max_score=maximum,
        )

    current_price = float(
        current_price
    )

    nearest_support = float(
        supports[0]["price"]
    )

    nearest_resistance = float(
        resistances[0]["price"]
    )

    long_risk = max(
        current_price
        - nearest_support,
        0.0,
    )

    long_reward = max(
        nearest_resistance
        - current_price,
        0.0,
    )

    short_risk = max(
        nearest_resistance
        - current_price,
        0.0,
    )

    short_reward = max(
        current_price
        - nearest_support,
        0.0,
    )

    long_rr = (
        long_reward
        / long_risk
        if long_risk > 0
        else None
    )

    short_rr = (
        short_reward
        / short_risk
        if short_risk > 0
        else None
    )

    if long_rr is not None:
        if long_rr >= 3.0:
            long_score = 5.0

        elif long_rr >= 2.0:
            long_score = 4.0

        elif long_rr >= 1.5:
            long_score = 3.0

        elif long_rr >= 1.0:
            long_score = 2.0

        if long_score:
            long_reasons.append(
                f"Local R/R {long_rr:.2f}"
            )

    if short_rr is not None:
        if short_rr >= 3.0:
            short_score = 5.0

        elif short_rr >= 2.0:
            short_score = 4.0

        elif short_rr >= 1.5:
            short_score = 3.0

        elif short_rr >= 1.0:
            short_score = 2.0

        if short_score:
            short_reasons.append(
                f"Local R/R {short_rr:.2f}"
            )

    return FactorScore(
        long=_clamp(
            long_score,
            0.0,
            maximum,
        ),

        short=_clamp(
            short_score,
            0.0,
            maximum,
        ),

        max_score=maximum,

        reasons_long=long_reasons,
        reasons_short=short_reasons,
    )


def calculate_confluence(
    *,
    indicators: dict[str, Any],
    structure: dict[str, Any],
    volume: dict[str, Any],
    orderflow: dict[str, Any],
    orderbook: dict[str, Any],
    derivatives: dict[str, Any],
    levels: dict[str, Any],
    volatility: dict[str, Any],
    regime: dict[str, Any],
) -> ConfluenceResult:
    factors = {
        "trend":
            _score_trend(
                indicators,
                regime,
            ),

        "structure":
            _score_structure(
                structure
            ),

        "momentum":
            _score_momentum(
                indicators
            ),

        "volume":
            _score_volume(
                volume,
                structure,
            ),

        "orderflow":
            _score_orderflow(
                orderflow
            ),

        "orderbook":
            _score_orderbook(
                orderbook
            ),

        "derivatives":
            _score_derivatives(
                derivatives
            ),

        "support_resistance":
            _score_support_resistance(
                levels
            ),

        "volatility":
            _score_volatility(
                volatility
            ),

        "risk_reward":
            _score_risk_reward(
                levels
            ),
    }

    long_score = sum(
        factor.long
        for factor
        in factors.values()
    )

    short_score = sum(
        factor.short
        for factor
        in factors.values()
    )

    long_score = round(
        _clamp(
            long_score,
            0.0,
            100.0,
        ),
        2,
    )

    short_score = round(
        _clamp(
            short_score,
            0.0,
            100.0,
        ),
        2,
    )

    score_difference = (
        long_score
        - short_score
    )

    if (
        long_score >= 60
        and score_difference >= 10
    ):
        setup_bias = (
            "LONG_BIAS"
        )

    elif (
        short_score >= 60
        and score_difference <= -10
    ):
        setup_bias = (
            "SHORT_BIAS"
        )

    else:
        setup_bias = (
            "NO_TRADE"
        )

    return ConfluenceResult(
        long_score=long_score,
        short_score=short_score,
        setup_bias=setup_bias,
        factors=factors,
    )