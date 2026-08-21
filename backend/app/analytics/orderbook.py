from __future__ import annotations


def analyze_orderbook(
    bids: list[list[float]],
    asks: list[list[float]],
    depth_levels: int = 20,
) -> dict:
    if not bids or not asks:
        return {
            "valid": False,
            "spread": None,
            "spread_bps": None,
            "imbalance": None,
        }

    normalized_bids = [
        [
            float(level[0]),
            float(level[1]),
        ]
        for level in bids[
            :depth_levels
        ]
    ]

    normalized_asks = [
        [
            float(level[0]),
            float(level[1]),
        ]
        for level in asks[
            :depth_levels
        ]
    ]

    best_bid = (
        normalized_bids[0]
    )

    best_ask = (
        normalized_asks[0]
    )

    best_bid_price = (
        best_bid[0]
    )

    best_bid_quantity = (
        best_bid[1]
    )

    best_ask_price = (
        best_ask[0]
    )

    best_ask_quantity = (
        best_ask[1]
    )

    mid_price = (
        best_bid_price
        + best_ask_price
    ) / 2.0

    spread = (
        best_ask_price
        - best_bid_price
    )

    spread_bps = (
        spread
        / mid_price
        * 10_000.0
        if mid_price
        else 0.0
    )

    bid_depth = sum(
        quantity
        for _,
        quantity
        in normalized_bids
    )

    ask_depth = sum(
        quantity
        for _,
        quantity
        in normalized_asks
    )

    total_depth = (
        bid_depth
        + ask_depth
    )

    imbalance = (
        (
            bid_depth
            - ask_depth
        )
        / total_depth
        if total_depth
        else 0.0
    )

    top_quantity_total = (
        best_bid_quantity
        + best_ask_quantity
    )

    microprice = (
        (
            best_ask_price
            * best_bid_quantity
            + best_bid_price
            * best_ask_quantity
        )
        / top_quantity_total
        if top_quantity_total
        else mid_price
    )

    bid_average = (
        bid_depth
        / len(
            normalized_bids
        )
    )

    ask_average = (
        ask_depth
        / len(
            normalized_asks
        )
    )

    bid_walls = [
        {
            "price": price,
            "quantity": quantity,
        }
        for price,
        quantity
        in normalized_bids
        if (
            bid_average > 0
            and quantity
            >= bid_average * 2.5
        )
    ]

    ask_walls = [
        {
            "price": price,
            "quantity": quantity,
        }
        for price,
        quantity
        in normalized_asks
        if (
            ask_average > 0
            and quantity
            >= ask_average * 2.5
        )
    ]

    pressure = "BALANCED"

    if imbalance >= 0.15:
        pressure = (
            "BID_PRESSURE"
        )

    elif imbalance <= -0.15:
        pressure = (
            "ASK_PRESSURE"
        )

    return {
        "valid": True,

        "best_bid":
            best_bid_price,

        "best_ask":
            best_ask_price,

        "mid_price":
            mid_price,

        "spread":
            spread,

        "spread_bps":
            spread_bps,

        "bid_depth":
            bid_depth,

        "ask_depth":
            ask_depth,

        "imbalance":
            imbalance,

        "microprice":
            microprice,

        "pressure":
            pressure,

        "bid_walls":
            bid_walls[:5],

        "ask_walls":
            ask_walls[:5],
    }